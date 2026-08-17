import sys

from agent import CodeActAgent
from executor import Interpreter
from llm_client import LLMClient

DEFAULT_TASK = (
    "Use wikipedia() to look up 'Python (programming language)'. Then count "
    "the words in the returned summary and print the count."
)


def main():
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_TASK

    llm = LLMClient()
    agent = CodeActAgent(llm, Interpreter())

    print(f"Task: {task}")
    result = agent.run(task)
    print(f"\nFinished: {result}")


if __name__ == "__main__":
    main()
