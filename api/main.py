"""NZZ ContextAI — FastAPI backend for the React frontend."""

import json
import math
import os
import sys
import threading
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from config import (
    CHROMA_PATH, CHROMA_COLLECTION,
    USE_RERANKING, EVAL_TOP_K_RETRIEVAL, EVAL_TOP_K_FINAL,
    LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_KEEP_ALIVE,
)
from embed import get_chroma_collection
from retrieval import load_models, retrieve
from generate import _build_context, _load_prompt

import ollama as _ollama

_state: dict = {}
_topics: list[str] = []   # filled by background thread after startup


def _generate_topics() -> None:
    """Sample the ChromaDB collection and ask the LLM for interesting questions."""
    global _topics
    try:
        col = _state.get("collection")
        if col is None:
            return

        sample = col.get(limit=500, include=["metadatas"])
        metas  = sample["metadatas"]

        # Pick top categories by article count
        cats     = Counter(m.get("category", "") for m in metas if m.get("category"))
        top_cats = [c for c, _ in cats.most_common(8) if c]

        # One representative title per category
        cat_titles: dict[str, str] = {}
        for m in metas:
            cat   = m.get("category", "")
            title = m.get("title", "")
            if cat in top_cats and cat not in cat_titles and len(title) > 15:
                cat_titles[cat] = title
            if len(cat_titles) >= 6:
                break

        if not cat_titles:
            return

        titles_str = "\n".join(f"- {t}" for t in cat_titles.values())
        resp = _ollama.chat(
            model=LLM_MODEL,
            keep_alive=LLM_KEEP_ALIVE,
            options={"temperature": 0.8, "num_predict": 220},
            messages=[{"role": "user", "content": (
                f"Hier sind Titel von NZZ-Artikeln aus verschiedenen Ressorts:\n{titles_str}\n\n"
                "Formuliere 4 interessante, unterschiedliche Fragen die ein NZZ-Leser stellen könnte. "
                "Jede Frage soll einen anderen inhaltlichen Schwerpunkt haben. "
                "Schreibe nur die 4 Fragen, jede auf einer eigenen Zeile, ohne Nummerierung."
            )}],
        )

        lines = [
            l.strip().lstrip("0123456789.-) •–")
            for l in resp.message.content.strip().splitlines()
            if l.strip()
        ]
        questions = [l for l in lines if len(l) > 10][:4]
        if questions:
            _topics = questions
            print(f"[topics] generated {len(_topics)} questions")

    except Exception as exc:
        print(f"[topics] generation failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _state["collection"] = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    _state["model"], _state["reranker"] = load_models(use_reranking=USE_RERANKING)
    _ollama.chat(
        model=LLM_MODEL,
        keep_alive=LLM_KEEP_ALIVE,
        messages=[{"role": "user", "content": "ping"}],
        options={"num_predict": 1},
    )
    # Generate example topics in the background so startup stays fast
    threading.Thread(target=_generate_topics, daemon=True).start()
    yield
    _state.clear()


app = FastAPI(title="NZZ ContextAI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Accept"],
)


class QueryRequest(BaseModel):
    question: str


def _to_pct(chunk: dict) -> int:
    if "rerank_score" in chunk:
        return round(1 / (1 + math.exp(-chunk["rerank_score"])) * 100)
    return round(chunk.get("similarity_score", 0) * 100)


def _format_date(iso: str) -> str:
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]
    try:
        y, m, d = iso.split("-")
        return f"{int(d)}. {months[int(m) - 1]} {y}"
    except Exception:
        return iso


def _build_sources(chunks: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for chunk in chunks:
        aid = chunk["article_id"]
        if aid not in seen or _to_pct(chunk) > _to_pct(seen[aid]):
            seen[aid] = chunk
    return [
        {
            "id":         i,
            "title":      chunk["title"],
            "date":       _format_date(chunk.get("published_date", "")),
            "snippet":    chunk["chunk_text"][:300].rstrip() + "…",
            "score":      _to_pct(chunk),
            "article_id": chunk["article_id"],
            "category":   chunk.get("category", ""),
            "author":     chunk.get("author", ""),
        }
        for i, chunk in enumerate(seen.values(), 1)
    ]


def _generate_follow_ups(question: str) -> list[str]:
    try:
        resp = _ollama.chat(
            model=LLM_MODEL,
            keep_alive=LLM_KEEP_ALIVE,
            options={"temperature": 0.7, "num_predict": 120},
            messages=[{
                "role": "user",
                "content": (
                    f"Basierend auf der Frage «{question}» – nenne 3 kurze Folgefragen "
                    "(je max. 10 Wörter), die ein NZZ-Leser stellen könnte. "
                    "Antworte nur mit den 3 Fragen, jede auf einer neuen Zeile, ohne Nummerierung."
                ),
            }],
        )
        lines = [l.strip(" -–•") for l in resp.message.content.strip().splitlines() if l.strip()]
        return [l for l in lines if l][:3]
    except Exception:
        return []


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.get("/health")
def health():
    return {"status": "ok", "model": LLM_MODEL}


@app.get("/topics")
def get_topics():
    """Return LLM-generated example questions derived from the archive content."""
    return {"de": _topics, "en": []}


@app.post("/query/stream")
def query_stream(req: QueryRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    def event_stream():
        chunks = retrieve(
            question,
            _state["model"],
            _state["collection"],
            _state["reranker"],
            top_k_retrieval=EVAL_TOP_K_RETRIEVAL,
            top_k_rerank=EVAL_TOP_K_FINAL,
        )

        system_prompt = _load_prompt("system_prompt.md")
        context = _build_context(chunks)
        user_message = f"Frage: {question}\n\nQuellen:\n{context}"

        for chunk in _ollama.chat(
            model=LLM_MODEL,
            options={"temperature": LLM_TEMPERATURE, "num_predict": LLM_MAX_TOKENS},
            keep_alive=LLM_KEEP_ALIVE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            stream=True,
        ):
            token = chunk.message.content
            if token:
                yield _sse({"type": "token", "content": token})

        sources    = _build_sources(chunks)
        follow_ups = _generate_follow_ups(question)
        yield _sse({"type": "done", "sources": sources, "followUps": follow_ups})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
