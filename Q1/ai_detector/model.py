"""Model training and persistence utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .paths import (
    METRICS_PATH,
    MODEL_PATH,
    SAMPLES_PATH,
    ensure_directories,
)


def build_pipeline() -> Pipeline:
    """Create the TF-IDF + Logistic Regression pipeline."""
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=25000,
        min_df=2,
    )
    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        solver="lbfgs",
        n_jobs=None,
    )
    return Pipeline(
        steps=[
            ("tfidf", vectorizer),
            ("clf", classifier),
        ]
    )


@dataclass
class TrainingReport:
    pipeline: Pipeline
    metrics: Dict[str, float]
    classification_report: Dict[str, Dict[str, float]]
    samples: pd.DataFrame


def train_detector(
    dataset: pd.DataFrame, test_size: float = 0.25, random_state: int = 42
) -> TrainingReport:
    """Train the detector and compute evaluation metrics."""
    if dataset.empty:
        raise ValueError("Dataset is empty – build_dataset must provide data.")
    X = dataset["text"].astype(str)
    y = dataset["label"].astype(str)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)
    ai_index = list(pipeline.classes_).index("ai")
    ai_probs = probabilities[:, ai_index]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision_ai": round(float(precision_score(y_test, predictions, pos_label="ai")), 4),
        "recall_ai": round(float(recall_score(y_test, predictions, pos_label="ai")), 4),
        "f1_ai": round(float(f1_score(y_test, predictions, pos_label="ai")), 4),
        "roc_auc": round(
            float(roc_auc_score((y_test == "ai").astype(int), ai_probs)), 4
        ),
    }
    cls_report = classification_report(y_test, predictions, output_dict=True)
    samples = pd.DataFrame(
        {
            "text": X_test,
            "label": y_test,
            "prediction": predictions,
            "ai_probability": ai_probs,
        }
    ).reset_index(drop=True)

    return TrainingReport(
        pipeline=pipeline,
        metrics=metrics,
        classification_report=cls_report,
        samples=samples,
    )


def save_model(pipeline: Pipeline, path=MODEL_PATH) -> str:
    ensure_directories(extra={path.parent})
    dump(pipeline, path)
    return str(path)


def save_metrics(
    metrics: Dict[str, float],
    cls_report: Dict[str, Dict[str, float]],
    path=METRICS_PATH,
) -> str:
    ensure_directories(extra={path.parent})
    payload = {"summary": metrics, "classification_report": cls_report}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)


def save_samples(samples: pd.DataFrame, path=SAMPLES_PATH, limit: int = 200) -> str:
    ensure_directories(extra={path.parent})
    samples.head(limit).to_csv(path, index=False)
    return str(path)


def load_trained_model(path=MODEL_PATH) -> Pipeline:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. Run aiot_hw5/Q1/train.py first."
        )
    return load(path)
