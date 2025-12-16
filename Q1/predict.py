"""CLI inference tool for the AI vs Human detector."""
from __future__ import annotations

import argparse
import json
import sys

from ai_detector.predictor import predict_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict whether text is AI or Human.")
    parser.add_argument(
        "--text",
        type=str,
        help="Text to evaluate. If omitted, the script reads from STDIN.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.text:
        text = args.text
    else:
        text = sys.stdin.read().strip()
    if not text:
        raise SystemExit("No text was provided for prediction.")
    result = predict_text(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

