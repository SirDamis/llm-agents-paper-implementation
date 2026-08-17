import re

from prompt import SYSTEM_PROMPT


def parse(text):
    thought = ""
    action = None
    args = ""
    content = None

    t = re.search(r"Thought:\s*([^\n]*)", text)
    if t:
        thought = t.group(1).strip()

    a = re.search(r"Action:\s*(\S+)[^\n]*", text)
    if a:
        body = a.group(0)[len("Action:"):].strip()
        tokens = body.split(None, 1)
        action = tokens[0]
        args = tokens[1] if len(tokens) > 1 else ""

    if action == "edit":
        eoe = re.search(r"end_of_edit", text)
        if eoe:
            nl = text.find("\n", a.start())
            if nl == -1:
                content = ""
            else:
                content = text[nl + 1:eoe.start()].strip("\n")
        else:
            content = None

    return thought, action, args, content


class SWEAgent:
    def __init__(self, model, env, issue, max_iterations=40):
        self.model = model
        self.env = env
        self.issue = issue
        self.max_iterations = max_iterations

    def run(self):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Issue:\n{self.issue}"},
        ]

        for step in range(1, self.max_iterations + 1):
            output = self.model.generate(messages)
            messages.append({"role": "assistant", "content": output})

            thought, action, args, content = parse(output)
            print(f"\n--- Step {step} ---")
            if thought:
                print(f"Thought: {thought}")

            if action is None:
                print("Action: (invalid format)")
                observation = "Invalid format. Output one Thought and one Action per turn."
                print(f"Observation: {observation}")
                messages.append({"role": "user", "content": f"Observation: {observation}"})
                continue

            print(f"Action: {action} {args}".rstrip())

            if action == "submit":
                observation = self.env.step(action, args, content)
                print(f"Observation:\n{observation}")
                return observation

            observation = self.env.step(action, args, content)
            print(f"Observation:\n{observation}")
            messages.append({"role": "user", "content": f"Observation:\n{observation}"})

        return "Stopped: reached maximum number of iterations."
