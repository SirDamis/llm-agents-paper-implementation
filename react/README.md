# ReAct (Minimal Implementation)

A minimal, readable implementation of **ReAct: Synergizing Reasoning and Acting in Language Models** (Yao et al., 2022, [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)).

The core idea of the paper is that LLMs reason better when they can **interleave reasoning (Thought) with acting (Action/Observation)**. Instead of producing a chain of thought in a vacuum, the model generates a thought, calls a tool to gather information, observes the result, and repeats — until it has enough evidence to emit a `Final Answer`. This implementation strips the paper's benchmarks (HotpotQA, ALFWorld, WebShop) down to that single loop.

## How it works

The agent runs a loop of **Thought → Action → Observation → ... → Final Answer**:

```
Question -> LLM -> Thought + Action -> Tool -> Observation -> LLM -> ... -> Final Answer
```

1. The system prompt ([`prompt.py`](prompt.py)) describes the available tools and the interleaved output format.
2. The agent ([`agent.py`](agent.py)) parses each LLM response and executes the action against the registered tools.
3. The full transcript (Thoughts, Actions, Observations) is kept in a [`Memory`](memory.py) and fed back to the LLM each turn.
4. The loop stops when the model emits `Final Answer:` or the iteration budget runs out.

## Output format

The model is expected to alternate between two modes:

```
Thought: I need to look up who was the first president of the US.
Action: wikipedia[George Washington]

Observation: <tool result>

Thought: I can answer now.
Final Answer: George Washington
```

## Project layout

```
react/
├── main.py        Entry point: wires LLM, tools, and agent together
├── agent.py       The ReAct loop (Thought/Action/Observation + memory)
├── llm_client.py  OpenAI-compatible chat client (config via env vars)
├── prompt.py      Builds the system prompt from the registered tools
├── tools.py       Tool registry with a safe calculator and a Wikipedia lookup
├── executor.py    Looks up and runs the action against the tools
├── parser.py      Regex parser for Thought/Action/Action Input/Final Answer
└── memory.py      Chat-history wrapper holding the reasoning trace
```

## Usage

Set up API credentials (an OpenAI-compatible endpoint):

```bash
API_URL=https://api.openai.com/v1
API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Ask a question:

```bash
python main.py "What is the capital of France?"
```

The agent prints its step-by-step trace (`Thought` / `Action` / `Observation`) and finishes with the final answer.

## Bundled tools

| Tool | Description |
| ---- | ----------- |
| `calculator` | Evaluates a mathematical expression via a restricted AST evaluator (no arbitrary code execution) |
| `wikipedia` | Fetches a short summary for a topic from Wikipedia's REST API |

Tools are plain dict entries in [`tools.py`](tools.py), so adding a new tool is a matter of writing a function and registering it — the system prompt updates automatically.

## References

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models.* arXiv:2210.03629.
