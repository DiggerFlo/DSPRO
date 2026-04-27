"""NZZ ContextAI — Streamlit Chat Interface"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import streamlit as st
import ollama

from config import (
    CHROMA_PATH, CHROMA_COLLECTION,
    USE_RERANKING, EVAL_TOP_K_RETRIEVAL, EVAL_TOP_K_FINAL,
    LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_KEEP_ALIVE,
)
from embed import get_chroma_collection
from retrieval import load_models, retrieve
from generate import _build_context, _load_prompt

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NZZ ContextAI",
    page_icon="📰",
    layout="wide",
)

# ── Models — einmal laden, danach gecacht ─────────────────────────────────────
@st.cache_resource(show_spinner="Modelle werden geladen...")
def load_pipeline():
    collection      = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    model, reranker = load_models(use_reranking=USE_RERANKING)
    # Ollama-Modell vorladen damit die erste Anfrage nicht kalt startet
    ollama.chat(
        model=LLM_MODEL,
        keep_alive=LLM_KEEP_ALIVE,
        messages=[{"role": "user", "content": "ping"}],
        options={"num_predict": 1},
    )
    return collection, model, reranker

collection, embed_model, reranker = load_pipeline()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📰 NZZ ContextAI")
    st.markdown("---")
    st.markdown("**Konfiguration**")
    st.caption(f"LLM:        `{LLM_MODEL}`")
    st.caption(f"Temperatur: `{LLM_TEMPERATURE}`")
    st.caption(f"Reranking:  `{'an' if USE_RERANKING else 'aus'}`")
    st.caption(f"Top-K:      `{EVAL_TOP_K_FINAL}` von `{EVAL_TOP_K_RETRIEVAL}`")
    st.caption(f"Chunks:     `{collection.count():,}`")
    st.markdown("---")
    if st.button("Gespräch zurücksetzen", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Archiv-Recherche")
st.caption("Stellen Sie Fragen zum NZZ-Archiv — die Antworten werden aus echten Artikeln generiert.")

# ── Chatverlauf anzeigen ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"Quellen ({len(msg['sources'])})", expanded=False):
                for i, chunk in enumerate(msg["sources"], 1):
                    score = chunk.get("rerank_score", chunk.get("similarity_score", 0))
                    st.markdown(
                        f"**[{i}] {chunk['title']}**  \n"
                        f"`{chunk['article_id']}` · {chunk.get('published_date', '—')} "
                        f"· {chunk.get('category', '')} · Score: `{score:.3f}`"
                    )

# ── Eingabe & Antwort ─────────────────────────────────────────────────────────
if query := st.chat_input("Ihre Frage an das NZZ-Archiv..."):

    # Nutzernachricht anzeigen
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Retrieval
    with st.spinner("Suche relevante Artikel..."):
        chunks = retrieve(
            query, embed_model, collection, reranker,
            top_k_retrieval=EVAL_TOP_K_RETRIEVAL,
            top_k_rerank=EVAL_TOP_K_FINAL,
        )

    # Antwort generieren (streaming)
    system_prompt = _load_prompt("system_prompt.md")
    context       = _build_context(chunks)
    user_message  = f"Frage: {query}\n\nQuellen:\n{context}"

    def _stream():
        for chunk in ollama.chat(
            model=LLM_MODEL,
            options={"temperature": LLM_TEMPERATURE, "num_predict": LLM_MAX_TOKENS},
            keep_alive=LLM_KEEP_ALIVE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            stream=True,
        ):
            yield chunk.message.content

    with st.chat_message("assistant"):
        answer = st.write_stream(_stream())
        with st.expander(f"Quellen ({len(chunks)})", expanded=True):
            for i, chunk in enumerate(chunks, 1):
                score = chunk.get("rerank_score", chunk.get("similarity_score", 0))
                st.markdown(
                    f"**[{i}] {chunk['title']}**  \n"
                    f"`{chunk['article_id']}` · {chunk.get('published_date', '—')} "
                    f"· {chunk.get('category', '')} · Score: `{score:.3f}`"
                )

    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "sources": chunks,
    })
