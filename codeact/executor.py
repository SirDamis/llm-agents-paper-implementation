import ast
import io
import json
import urllib.parse
import urllib.request
from contextlib import redirect_stdout

MAX_OUTPUT = 4000


def _wikipedia(query):
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + urllib.parse.quote(query)
    )
    req = urllib.request.Request(url, headers={"User-Agent": "codeact-minimal/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return data.get("extract") or "No summary found."


class Interpreter:
    """A persistent Python interpreter: state (variables, imports,
    definitions) survives across turns."""

    def __init__(self):
        self.namespace = {"wikipedia": _wikipedia}

    def run(self, code):
        stdout = io.StringIO()
        try:
            tree = ast.parse(code)
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last = tree.body.pop()
                with redirect_stdout(stdout):
                    exec(compile(tree, "<codeact>", "exec"), self.namespace)
                    value = eval(
                        compile(ast.Expression(last.value), "<codeact>", "eval"),
                        self.namespace,
                    )
                tail = repr(value)
            else:
                with redirect_stdout(stdout):
                    exec(compile(tree, "<codeact>", "exec"), self.namespace)
                tail = ""

            parts = [p for p in (stdout.getvalue().rstrip(), tail) if p]
            output = "\n".join(parts) or "(no output)"
        except Exception as e:
            output = f"{type(e).__name__}: {e}"

        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + "\n(output truncated)"
        return output
