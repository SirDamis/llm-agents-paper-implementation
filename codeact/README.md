# CodeAct (Minimal Implementation)

A minimal, readable implementation of **Executable Code Actions Elicit Better LLM Agents** (Wang et al., 2024, [arXiv:2402.01030](https://arxiv.org/abs/2402.01030)).

The core idea of the paper is that LLM agents act more effectively when actions are expressed as **executable Python code** rather than as JSON or function calls. Code is a natural, composable action language: it can express complex multi-step behavior (loops, conditionals, calling several tools at once) in a single turn, and the observation space stays unified — text, numbers, data structures, and images all come back as interpreter results. This implementation strips the paper's benchmarks (MINT, ALFWorld, WebArena) down to that single idea.

## How it works

The agent runs a loop of **Code → Execute → Observe**:

```
Task -> LLM -> ```python ...``` -> Interpreter -> Observation -> LLM -> ... -> Finished
```

1. The system prompt ([`prompt.py`](prompt.py)) instructs the model to output fenced Python code blocks.
2. The agent ([`agent.py`](agent.py)) extracts the block and hands it to a **persistent interpreter**.
3. The interpreter ([`executor.py`](executor.py)) executes the code in a shared namespace: variables, imports, and definitions **survive across turns**, so the agent can build a solution incrementally. It returns stdout, the repr of the last expression, and any exception as the observation.
4. The loop ends when the model outputs `Finished: <summary>` instead of code.

## Why persistence matters

This is the key difference from ReAct-style tool agents. In ReAct, every turn is stateless: the model must re-argue state into each action. In CodeAct, a turn can be:

```python
summary = wikipedia("Python (programming language)")
```

and the *next* turn can just reference `summary` — the interpreter remembers it. The agent decomposes one task into a sequence of small, composable code steps.

## Project layout

```
codeact/
├── main.py        Entry point: wires LLM and interpreter together
├── agent.py       The CodeAct loop (code -> execute -> observe)
├── llm_client.py  OpenAI-compatible chat client (config via env vars)
├── executor.py    Persistent Python interpreter + tool functions
└── prompt.py      System prompt describing code output format
```

## Usage

Set up API credentials (an OpenAI-compatible endpoint):

```bash
API_URL=https://api.openai.com/v1
API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Run with the default multi-step task:

```bash
python main.py
```

Or give it your own task:

```bash
python main.py "Compute the first 100 digits of pi and save them to pi.txt"
```

The agent prints each code snippet and its observation, ending with `Finished: <summary>`.

## Bundled tools

A `wikipedia(query)` function is injected into the interpreter's namespace, demonstrating how tools become plain callables in code — the agent can call it mid-expression, wrap it in loops, or chain it with other logic.

## References

- Wang, X., Chen, Y., Yuan, L., Zhang, Y., Li, Y., Peng, H., & Ji, H. (2024). *Executable Code Actions Elicit Better LLM Agents.* arXiv:2402.01030.
