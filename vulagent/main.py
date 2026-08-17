import json
import os
import sys

from llm_client import LLMClient
from pipeline import run_pipeline

DEFAULT_SAMPLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "demo", "vulnerable.c"
)


def _number_lines(text):
    return "".join(f"L{i + 1}: {line}" for i, line in enumerate(text.splitlines(keepends=True)))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SAMPLE

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        code = _number_lines(f.read())

    print(f"Analyzing {path}")
    report = run_pipeline(LLMClient(), code)
    print("\n=== FINAL REPORT ===")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
