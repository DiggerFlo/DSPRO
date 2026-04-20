"""Generate reference answers for ground truth entries using the full article text.

Run once before experiment.py to populate expected_answer fields:
    python scripts/build_expected_answers.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import ollama
from preprocess import _load_nzz_json
from config import EVAL_GROUND_TRUTH, LLM_MODEL, LLM_TEMPERATURE

_SYSTEM = (
    "Du bist ein Recherche-Assistent. Beantworte die folgende Frage "
    "ausschliesslich auf Basis des bereitgestellten Artikels. "
    "Schreibe 3–5 Sätze auf Deutsch, sachlich und präzise."
)


_MAX_ARTICLE_CHARS = 4000  # verhindert Context-Overflow bei langen Artikeln


def _generate(query: str, article_text: str) -> str:
    truncated = article_text[:_MAX_ARTICLE_CHARS]
    response = ollama.chat(
        model=LLM_MODEL,
        options={"temperature": 0.1, "num_predict": 800},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Frage: {query}\n\nArtikel:\n{truncated}"},
        ],
    )
    return response.message.content.strip()


def main() -> None:
    print("Lade Artikel...")
    df = _load_nzz_json()
    article_map = {row["article_id"]: row for _, row in df.iterrows()}

    with open(EVAL_GROUND_TRUTH, "r", encoding="utf-8") as f:
        samples = [json.loads(line) for line in f if line.strip()]

    updated = 0
    for i, sample in enumerate(samples, 1):
        if len(sample.get("expected_answer") or "") > 80:
            print(f"[{i}/{len(samples)}] Bereits vorhanden — übersprungen")
            continue

        article_id = sample["relevant_article_ids"][0]
        article = article_map.get(article_id)
        if article is None:
            print(f"[{i}/{len(samples)}] Artikel {article_id} nicht gefunden — übersprungen")
            continue

        article_text = f"{article['title']}\n\n{article['body']}"
        print(f"[{i}/{len(samples)}] {sample['query'][:65]}...")
        sample["expected_answer"] = _generate(sample["query"], article_text)
        updated += 1

    with open(EVAL_GROUND_TRUTH, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"\n✓ {updated} Referenzantworten generiert und in ground_truth.jsonl gespeichert.")


if __name__ == "__main__":
    main()
