import re

from prompt import SYSTEM_PROMPT


def parse(text):
    finished = re.search(r"Finished:\s*(.*)", text, re.DOTALL)
    if finished:
        return None, finished.group(1).strip()

    block = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if not block:
        return None, None
    return block.group(1).strip(), None


class CodeActAgent:
    def __init__(self, llm, interpreter, max_iterations=10):
        self.llm = llm
        self.interpreter = interpreter
        self.max_iterations = max_iterations

    def run(self, task):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Task:\n{task}"},
        ]

        for step in range(1, self.max_iterations + 1):
            output = self.llm.generate(messages)
            messages.append({"role": "assistant", "content": output})

            code, finished = parse(output)
            print(f"\n--- Step {step} ---")

            if finished is not None:
                print(f"Finished: {finished}")
                return finished

            if code is None:
                print("Action: (invalid format)")
                observation = (
                    "Invalid format. Output a python code block or "
                    "`Finished: <summary>`."
                )
                print(f"Observation: {observation}")
                messages.append({"role": "user", "content": f"Observation: {observation}"})
                continue

            print(f"Code:\n{code}")
            observation = self.interpreter.run(code)
            print(f"Observation:\n{observation}")
            messages.append({"role": "user", "content": f"Observation:\n{observation}"})

        return "Stopped: reached maximum number of iterations."
