from executor import execute
from memory import Memory
from parser import parse


class ReActAgent:
    def __init__(self, llm, tools, system_prompt, max_iterations=5):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations

    def run(self, question):
        memory = Memory(self.system_prompt)
        memory.add_user(question)

        for step in range(1, self.max_iterations + 1):
            output = self.llm.generate(memory.messages)
            memory.add_assistant(output)

            parsed = parse(output)
            print(f"\n--- Step {step} ---")
            if parsed.thought:
                print(f"Thought: {parsed.thought}")

            if parsed.final_answer is not None:
                print(f"Final Answer: {parsed.final_answer}")
                return parsed.final_answer

            if parsed.action is None:
                print("Action: (invalid format)")
                memory.add_user(
                    "Observation: Invalid format. Output Thought, Action, and Action Input."
                )
                continue

            print(f"Action: {parsed.action}[{parsed.action_input}]")

            observation = execute(parsed.action, parsed.action_input, self.tools)
            print(f"Observation: {observation}")
            memory.add_user(f"Observation: {observation}")

        return "Stopped: reached maximum number of iterations."
