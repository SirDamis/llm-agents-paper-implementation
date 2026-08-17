import sys

from agent import ReActAgent
from llm_client import LLMClient
from prompt import build_system_prompt
from tools import TOOLS


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <question>")
        sys.exit(1)
    question = sys.argv[1]
    llm = LLMClient()
    agent = ReActAgent(llm, TOOLS, build_system_prompt(TOOLS))
    print(f"Question: {question}")
    print(f"Answer: {agent.run(question)}")


if __name__ == "__main__":
    main()
