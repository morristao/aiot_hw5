"""Inference helpers used by the CLI and Streamlit demo."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict

from sklearn.pipeline import Pipeline

from .model import load_trained_model
from .paths import METRICS_PATH


@lru_cache(maxsize=1)
def _cached_model() -> Pipeline:
    return load_trained_model()


def predict_text(text: str) -> Dict[str, float | str]:
    """Return AI and Human probabilities for a piece of text."""
    clean_text = (text or "").strip()
    if not clean_text:
        raise ValueError("Input text cannot be empty.")

    pipeline = _cached_model()
    probabilities = pipeline.predict_proba([clean_text])[0]
    classes = list(pipeline.classes_)
    ai_index = classes.index("ai")
    ai_probability = float(probabilities[ai_index])

    return {
        "label": "ai" if ai_probability >= 0.5 else "human",
        "ai_probability": ai_probability,
        "human_probability": 1.0 - ai_probability,
    }


def load_metrics() -> Dict[str, float]:
    """Read the saved metrics JSON if it exists."""
    path = Path(METRICS_PATH)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

