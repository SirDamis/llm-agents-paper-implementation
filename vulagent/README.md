# VulAgent (Minimal Implementation)

A minimal, readable implementation of **VulAgent: Hypothesis-Validation Driven Multi-Agent Architecture for Vulnerability Detection** (Wang et al., 2026, [arXiv:2509.11523](https://arxiv.org/abs/2509.11523)).

The core idea of the paper is that LLM vulnerability detectors over-report: they flag speculative risks without checking whether the alleged exploit is actually possible. VulAgent mimics how human security auditors work — form a hypothesis about a suspected vulnerability, then try to validate (or refute) it against the surrounding code before reporting it. This implementation strips the paper's datasets (PrimeVul, SVEN) and static-analysis tooling (Joern) down to that pipeline.

## How it works

A five-stage pipeline, all operating on line-numbered code (`L1: ...`) so agents can reference exact lines:

```
MetaAgent (dispatch) -> Analyzers (multi-view) -> Aggregator (dedupe)
  -> TriggerPlanner (hypothesis) -> AssumptionPruner (conditions)
  -> FinalValidator (path guards) -> final report
```

1. **MetaAgent** reads the code's semantic cues (memory ops, format strings, file I/O, auth, crypto, concurrency, injection...) and activates a minimal set of specialized analyzers. Three always run — `static_analyzer`, `behavior_analyzer`, `memory_layout` — the paper's safety net.
2. **Analyzers** each scan from one perspective with a role-specific prompt and a strict JSON output contract. Deliberately tuned for **maximum recall**: raw reports are noisy candidates.
3. **AggregatorAgent** (LLM) merges semantically identical findings across analyzers: same CWE + overlapping line spans are grouped and unified (one description, unioned lines and source agents); distinct issues are preserved.
4. **TriggerPlanner** turns each candidate into a **falsifiable hypothesis** `(cwe, conditions, trigger_path)`: a path from an attacker-controllable source to the sink, with every guard encountered recorded as a *condition* — never used to prune.
5. **AssumptionPruner** validates each condition against the code context, classifying it `valid / contradicted / plausible`; a contradicted condition kills the hypothesis cheaply.
6. **FinalValidator** applies **guard-dominance**: a path is discarded only if pre-sink defenses (bounds checks, early returns, sanitization) block *all* feasible routes; otherwise retained. Emits the final verdict.


## Project layout

```
vulagent/
├── main.py        Entry point: line-numbers the source file, runs the pipeline
├── pipeline.py    Orchestration of the five stages + JSON parsing + aggregation
├── prompts.py     System prompts for every agent role (incl. analyzer registry)
├── llm_client.py  OpenAI-compatible chat client (config via env vars)
└── demo/          Sample C files: a vulnerable and a fixed buffer copy
```

## Usage

Set up API credentials (an OpenAI-compatible endpoint):

```bash
API_URL=https://api.openai.com/v1
API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Run against the bundled vulnerable sample:

```bash
python main.py
```

Or any C/C++ file:

```bash
python main.py path/to/code.c
```

Every stage prints its output (activated analyzers, findings, merged candidates, hypotheses, condition verdicts, path verdicts), ending with the final JSON report: `vulnerability_reported`, `cwe_list`, and per-CWE `path_valid` decisions. Try `demo/safe.c` to see the validation stages prune the same candidate.

## References

- Wang, Z., Li, G., Li, J., Zhu, H., & Jin, Z. (2026). *VulAgent: Hypothesis-Validation Driven Multi-Agent Architecture for Vulnerability Detection.* Findings of ACL 2026. arXiv:2509.11523.
