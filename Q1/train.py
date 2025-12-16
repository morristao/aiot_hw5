"""Training entry-point for the AI vs Human detector."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_detector import data, model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the AI vs Human detector")
    parser.add_argument(
        "--limit-per-label",
        type=int,
        default=4000,
        help="Maximum number of samples to keep for each class (ai/human).",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Test split ratio for evaluation.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for train/test split reproducibility.",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Re-download the HC3 dataset even if a cached copy exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.force_download:
        data.download_raw_dataset(force=True)
    dataset = data.load_dataset(limit_per_label=args.limit_per_label)
    training_report = model.train_detector(
        dataset, test_size=args.test_size, random_state=args.random_state
    )
    model_path = model.save_model(training_report.pipeline)
    metrics_path = model.save_metrics(
        training_report.metrics, training_report.classification_report
    )
    samples_path = model.save_samples(training_report.samples)

    summary = {
        "model_path": model_path,
        "metrics_path": metrics_path,
        "samples_preview": samples_path,
        "metrics": training_report.metrics,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

