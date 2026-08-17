import os
import sys

from agent import SWEAgent
from environment import Environment
from model import Model

DEMO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo")

DEMO_ISSUE = (
    "The `total` function is supposed to return the sum of all numbers in "
    "`prices`, but it currently returns the wrong result. Locate the bug, fix "
    "it, and submit your patch."
)


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else DEMO_DIR
    issue = sys.argv[2] if len(sys.argv) > 2 else DEMO_ISSUE

    model = Model()
    env = Environment(root=repo)
    agent = SWEAgent(model, env, issue)

    print(f"Repo: {repo}")
    print(f"Issue: {issue}")
    result = agent.run()
    print(f"\nResult:\n{result}")


if __name__ == "__main__":
    main()
