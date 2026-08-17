import re
from dataclasses import dataclass


@dataclass
class Parsed:
    thought: str = ""
    action: str = None
    action_input: str = None
    final_answer: str = None


_FINAL = re.compile(r"Final Answer:\s*(.*)", re.DOTALL)
_ACTION = re.compile(r"Action:\s*(\S+)")
_ACTION_INPUT = re.compile(r"Action Input:\s*(.+)")
_THOUGHT = re.compile(r"Thought:\s*(.*?)(?=\n\s*(?:Action|Final Answer):|\Z)", re.DOTALL)


def parse(text):
    final = _FINAL.search(text)
    if final:
        return Parsed(final_answer=final.group(1).strip())

    action = _ACTION.search(text)
    action_input = _ACTION_INPUT.search(text)

    name = action.group(1) if action else None
    inp = action_input.group(1).strip() if action_input else None

    if name and "[" in name:
        name, inner = name.split("[", 1)
        inp = inner.rsplit("]", 1)[0] if "]" in inner else inner

    thought = _THOUGHT.search(text)

    return Parsed(
        thought=thought.group(1).strip() if thought else "",
        action=name,
        action_input=inp,
    )
