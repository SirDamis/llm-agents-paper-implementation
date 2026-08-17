import os
import sys

from llm_client import LLMClient
from pipeline import run_pipeline

DEMO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo")


def _read(path_or_default):
    return open(path_or_default, "r", encoding="utf-8").read()


def main():
    diff_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DEMO_DIR, "diff.txt")
    message_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DEMO_DIR, "commit_message.txt")

    diff = _read(diff_path)
    commit_message = _read(message_path).strip()

    print(f"Commit message: {commit_message}")
    print(f"Diff:\n{diff}")

    report = run_pipeline(LLMClient(), diff, commit_message)
    print("\n=== FINAL REVIEW COMMENTS ===")
    print(report["final_comments"])


if __name__ == "__main__":
    main()