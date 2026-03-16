"""Preprocessing pipeline — cleans and normalizes raw articles."""

import re
import pandas as pd
from config import DATA_SOURCE, KAGGLE_TRAIN, KAGGLE_TEST, MIN_TEXT_LENGTH

def load_dataset(split: str = "train") -> pd.DataFrame:
    if DATA_SOURCE == "kaggle":
        path = KAGGLE_TRAIN if split == "train" else KAGGLE_TEST
        return _load_kaggle(path)
    elif DATA_SOURCE == "nzz_api":
        return _load_nzz_api(split)
    else:
        raise ValueError(f"Unbekannte DATA_SOURCE: {DATA_SOURCE}")

def _load_kaggle(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";", 1)
            if len(parts) == 2:
                rows.append({"category": parts[0], "text": parts[1]})
    return pd.DataFrame(rows)

def _load_nzz_api(split: str) -> pd.DataFrame:
    # Platzhalter für späteren NZZ API Connector
    raise NotImplementedError("NZZ API noch nicht implementiert.")

def extract_title_and_body(text: str) -> tuple[str, str]:
    parts = text.split(". ", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return text[:80].strip(), text.strip()

def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].str.len() > MIN_TEXT_LENGTH]
    df[["title", "body"]] = df["text"].apply(
        lambda t: pd.Series(extract_title_and_body(t))
    )
    df = df.drop(columns=["text"])
    df = df.reset_index(drop=True)
    return df