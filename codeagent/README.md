# CodeAgent (Minimal Implementation)

A minimal, readable implementation of **CodeAgent: Autonomous Communicative Agents for Code Review** (Tang et al., 2024, [arXiv:2402.02172](https://arxiv.org/abs/2402.02172)).

The core idea of the paper is that code review is inherently *collaborative and conversational*, but existing automation treats it as single input→output generation. CodeAgent simulates a human review team as role-played agents that *actually converse*, supervised by a **QA-Checker** that keeps conversations from drifting off the original review question. This implementation strips the paper's dataset (3,545 commits, 9 languages) down to that pipeline.

## How it works

A waterfall of four phases, each broken into atomic two-agent conversations (instructor → assistant). Every conversation is supervised by the QA-Checker:

```
diff + commit message
  → Phase 1: Basic Info Sync    (CEO ↔ Coder: language, modality)
  → Phase 2: Code Review        (Reviewer ↔ Coder: CA, VA, FA)
  → Phase 3: Code Alignment     (Reviewer ↔ Coder: revision)
  → Phase 4: Document           (CEO ↔ CPO: final comments)
```

1. **The roles** ([`prompts.py`](prompts.py)) — CEO, CTO, CPO, Reviewer, Coder — each with a role card describing their responsibility in the team.
2. **Atomic conversations** ([`conversation.py`](conversation.py)) — one instructor asks a focused question (e.g., "does the commit message match the change?"), one assistant answers.
3. **QA-Checker** — the paper's key contribution. After each answer, it decides whether the answer actually addresses the original question. If not, it generates an *additional instruction* that gets appended to the question and the assistant re-answers — `q₁ = q₀ + instruction` — looping until on-topic or the turn budget runs out. This is the anti-*prompt drifting* mechanism that the paper's ablation shows is critical (vulnerability confirmation rate 92.96% with it vs 73.23% without).
4. **The four phases** ([`pipeline.py`](pipeline.py)) — sync context → review (consistency **CA**, vulnerability **VA**, format **FA**) → align/revise (**CR**) → document final conclusions.

## Project layout

```
codeagent/
├── main.py         Entry point: reads diff + commit message, runs the pipeline
├── pipeline.py     The 4-phase waterfall orchestration
├── conversation.py Atomic two-agent conversation + QA-Checker supervisor
├── prompts.py      Role cards and QA-Checker system prompt
├── llm_client.py   OpenAI-compatible chat client (config via env vars)
└── demo/           A diff and commit message with seeded issues
```

## Usage

Set up API credentials (an OpenAI-compatible endpoint):

```bash
API_URL=https://api.openai.com/v1
API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Run against the bundled demo (a commit message claiming sanitization that actually introduces a command-injection bug):

```bash
python main.py
```

Or provide your own diff and commit message:

```bash
python main.py path/to/diff.txt "commit message text"
```

Each phase prints its conversation output and any QA-Checker re-asks, ending with the synthesized final review comments.

## References

- Tang, X., Kim, K., Song, Y., et al. (2024). *CodeAgent: Autonomous Communicative Agents for Code Review.* arXiv:2402.02172.