"""Preprocessing pipeline — cleans and normalizes raw articles."""

import re
import glob
import json
from bs4 import BeautifulSoup
import pandas as pd
from config import MIN_TEXT_LENGTH, NZZ_JSON_GLOB


# ── HTML Stripping ────────────────────────────────────────────────────────────

def strip_html(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_dataset() -> pd.DataFrame:
    return _load_nzz_json()


def _load_nzz_json(glob_pattern: str = None) -> pd.DataFrame:
    """Lädt NZZ-JSON-Dateien und gibt ein normalisiertes DataFrame zurück.

    Args:
        glob_pattern: Optionales Glob-Muster, z.B. für einen einzelnen Monat.
                      Wenn None, wird NZZ_JSON_GLOB aus config verwendet.
    """
    pattern = glob_pattern or NZZ_JSON_GLOB
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Keine NZZ-JSON-Dateien gefunden unter: {pattern}")

    rows = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Struktur kann sein:
        #   { "result": [...] }          → direkte Objekt-Antwort
        #   [ { "result": [...] } ]      → Objekt in einer Liste verpackt
        if isinstance(data, list):
            articles = data[0].get("result", []) if data else []
        else:
            articles = data.get("result", [])

        for art in articles:
            title = art.get("ueberschrift_ctx", "").strip()
            lead  = art.get("vorspann_ctx", "").strip()
            body_html = art.get("grundtext_ctx", "")
            body  = strip_html(body_html)

            # Vorspann dem Body voranstellen damit er mit eingebettet wird
            full_body = (lead + " " + body).strip() if lead else body

            rows.append({
                "article_id":     str(art.get("media_id", "")),
                "title":          title,
                "lead":           lead,
                "body":           full_body,
                "category":       art.get("lt_ressort_name", ""),
                "subcategory":    art.get("lt_unterressort_name", ""),
                "author":         art.get("autor_ctx", ""),
                "published_date": (art.get("published_from_ts") or [""])[0][:10],  # YYYY-MM-DD
                "zeitung":        (art.get("zeitung_name") or ["nzz.ch"])[0],
            })

    return pd.DataFrame(rows)


def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Preprocessing Pipeline ────────────────────────────────────────────────────

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["body"])
    df["body"] = df["body"].apply(clean_text)
    df = df[df["body"].str.len() > MIN_TEXT_LENGTH]
    df = df.reset_index(drop=True)
    return df
