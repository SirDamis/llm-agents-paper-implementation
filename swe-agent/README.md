# SWE-Agent (Minimal Implementation)

A minimal, readable implementation of **SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering** (Yang et al., 2024, [arXiv:2405.15793](https://arxiv.org/abs/2405.15793)).

The core idea of the paper is that LLMs work better at software engineering tasks when they interact with the repository through a purpose-built **Agent-Computer Interface (ACI)** — a small set of curated commands that return compact, summarized feedback — instead of being handed raw shell output. This implementation strips the paper's full system (Docker sandboxes, fine-tuned models, SWE-bench evaluation) down to that single idea.

## How it works

The agent runs a loop of **Thought → Action → Observation**:

```
Issue -> LLM -> Thought + Action -> Environment (ACI) -> Observation -> LLM -> ...
```

1. The system prompt ([`prompt.py`](prompt.py)) describes the available commands and the strict `Thought:` / `Action:` output format.
2. The agent ([`agent.py`](agent.py)) parses each LLM response, executes the action against the environment, and feeds the observation back into the conversation.
3. The environment ([`environment.py`](environment.py)) is the ACI: a filesystem sandbox whose actions return **summarized, limited output** rather than raw dumps.

## The ACI commands

| Command | Purpose |
| ------- | ------- |
| `search_dir "<term>" [<dir>]` | Grep a directory, capped results per file |
| `search_file "<term>" [<file>]` | Grep a single file |
| `find_file "<name>" [<dir>]` | List files whose path contains `<name>` |
| `open "<path>" [<line>]` | Open a file with a 30-line window around the cursor |
| `goto <line>` | Re-center the window on a line |
| `scroll_up` / `scroll_down` | Move the window up/down |
| `edit <start>:<end>` | Replace a line range with content terminated by `end_of_edit` |
| `submit` | Write all edits back to disk and return the diff |

Everything the agent sees is a bounded window of a file or a truncated search result — this is the key ACI design choice that keeps the LLM's context focused.

## Project layout

```
swe-agent/
├── main.py         Entry point: wires model, environment, and agent together
├── agent.py        ReAct-style loop + Thought/Action parser
├── environment.py  The ACI: summarized filesystem actions
├── model.py        OpenAI-compatible chat client (config via env vars)
├── prompt.py       System prompt describing commands and output format
└── demo/           Tiny buggy repo the agent can fix out of the box
```

## Usage

Set up API credentials (an OpenAI-compatible endpoint):

```bash
API_URL=https://api.openai.com/v1
API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Run against the bundled demo repo:

```bash
python main.py
```

Run against your own repo and issue:

```bash
python main.py /path/to/repo "Describe the bug to fix here..."
```

The agent prints its step-by-step trace (`Thought` / `Action` / `Observation`). When it finishes with `submit`, the patch is applied to the files on disk and the generated diff is printed.

## Demo

The [`demo/`](demo) directory contains a tiny in-memory user store with deliberately seeded bugs, plus a test file. It lets you watch the agent explore, find the bugs, and submit a patch in a couple of iterations.

## References

- Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., & Press, O. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering.* arXiv:2405.15793.
