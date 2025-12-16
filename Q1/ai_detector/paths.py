"""Centralized path helpers for the AI vs Human detector project."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

BASE_DIR: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"
REPORTS_DIR: Path = BASE_DIR / "reports"

RAW_DATA_PATH: Path = RAW_DATA_DIR / "open_qa.jsonl"
PROCESSED_DATASET_PATH: Path = PROCESSED_DATA_DIR / "ai_human_dataset.csv"
MODEL_PATH: Path = ARTIFACTS_DIR / "ai_human_detector.joblib"
METRICS_PATH: Path = REPORTS_DIR / "metrics.json"
SAMPLES_PATH: Path = REPORTS_DIR / "sample_predictions.csv"

HC3_OPEN_QA_URL = (
    "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/open_qa.jsonl"
)


def ensure_directories(extra: Iterable[Path] | None = None) -> None:
    """Ensure that every required directory exists."""
    directories = {
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        ARTIFACTS_DIR,
        REPORTS_DIR,
    }
    if extra:
        directories.update(extra)
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

