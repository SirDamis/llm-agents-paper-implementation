import ast
import json
import operator as op
import urllib.parse
import urllib.request


class Tool:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def run(self, action_input):
        return self.func(action_input)


_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.BinOp):
        return _BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand)
    if isinstance(node, ast.Constant):
        return node.value
    raise ValueError("unsupported expression")



def calculator(expression):
    return str(_eval(ast.parse(expression, mode="eval")))


def wikipedia(query):
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + urllib.parse.quote(query)
    )
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    return data.get("extract") or "No summary found."


TOOLS = {
    "calculator": Tool(
        "calculator",
        "Evaluate a mathematical expression. Input: an arithmetic expression.",
        calculator,
    ),
    "wikipedia": Tool(
        "wikipedia",
        "Look up a topic on Wikipedia and return a short summary. Input: a topic name.",
        wikipedia,
    ),
}
