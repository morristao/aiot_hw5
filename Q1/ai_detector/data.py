"""Data handling helpers for the AI vs Human detector."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import requests

from .paths import (
    HC3_OPEN_QA_URL,
    PROCESSED_DATASET_PATH,
    RAW_DATA_PATH,
    ensure_directories,
)


def download_raw_dataset(force: bool = False, url: str = HC3_OPEN_QA_URL) -> Path:
    """Download the HC3 open QA split to the raw data directory."""
    ensure_directories()
    if RAW_DATA_PATH.exists() and not force:
        return RAW_DATA_PATH

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    RAW_DATA_PATH.write_bytes(response.content)
    return RAW_DATA_PATH


def _clean_text(text: str) -> str:
    text = (text or "").strip()
    return " ".join(text.split())


def _flatten_answers(records: Iterable[dict], limit_per_label: int | None) -> pd.DataFrame:
    rows: List[dict] = []

    def append_rows(samples: Iterable[str], label: str) -> None:
        for text in samples:
            clean = _clean_text(text)
            if not clean:
                continue
            rows.append({"text": clean, "label": label})

    for record in records:
        append_rows(record.get("human_answers", []), "human")
        append_rows(record.get("chatgpt_answers", []), "ai")

    df = pd.DataFrame(rows).drop_duplicates()
    if limit_per_label:
        balanced = []
        rng = random.Random(42)
        for label in ("ai", "human"):
            subset = df[df["label"] == label]
            if subset.empty:
                continue
            if len(subset) > limit_per_label:
                sampled = subset.sample(limit_per_label, random_state=rng.randint(0, 2**32 - 1))
            else:
                sampled = subset
            balanced.append(sampled)
        if balanced:
            df = pd.concat(balanced, ignore_index=True)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df


def build_dataset(limit_per_label: int = 4000, force: bool = False) -> pd.DataFrame:
    """Create a processed CSV dataset from the raw JSONL file."""
    raw_path = download_raw_dataset(force=force)
    records: List[dict] = []
    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    df = _flatten_answers(records, limit_per_label=limit_per_label)
    ensure_directories(extra={PROCESSED_DATASET_PATH.parent})
    df.to_csv(PROCESSED_DATASET_PATH, index=False)
    return df


def load_dataset(limit_per_label: int = 4000) -> pd.DataFrame:
    """Load the processed dataset, building it if necessary."""
    if PROCESSED_DATASET_PATH.exists():
        return pd.read_csv(PROCESSED_DATASET_PATH)
    return build_dataset(limit_per_label=limit_per_label)

