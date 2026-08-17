# LLM Agents

This repository contains minimal implementations of different LLM agents papers and ideas. Each agent is organized in its own folder and focuses on the core idea of the corresponding paper, stripping away implementation details to keep the code easy to read and adapt. A curated list of the referenced papers is included below.

## Agents

| Agent | Folder | Description |
| ----- | ------ | ----------- |
| ReAct | [`react`](./react) | Synergizes reasoning and acting via interleaved thought-action traces. |
| SWE-Agent | [`swe-agent`](./swe-agent) | Agent-computer interface for LLM-driven software engineering. |
| CodeAct | [`codeact`](./codeact) | Uses executable code as a unified action space. |
| CodeAgent | [`codeagent`](./codeagent) | Role-played review team whose QA-Checker supervises conversations against topic drift. |
| VulAgent | [`vulagent`](./vulagent) | Hypothesis-validation driven multi-agent vulnerability detection. |

## Papers

- **ReAct** — *ReAct: Synergizing Reasoning and Acting in Language Models* (Yao et al., 2022) — [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- **SWE-Agent** — *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering* (Yang et al., 2024) — [arXiv:2405.15793](https://arxiv.org/abs/2405.15793)
- **CodeAct** — *Executable Code Actions Elicit Better LLM Agents* (Wang et al., 2024) — [arXiv:2402.01030](https://arxiv.org/abs/2402.01030)
- **CodeAgent** — *CodeAgent: Autonomous Communicative Agents for Code Review* (Tang et al., 2024) — [arXiv:2402.02172](https://arxiv.org/abs/2402.02172)
- **VulAgent** — *VulAgent: Hypothesis-Validation Driven Multi-Agent Architecture for Vulnerability Detection* (Wang et al., 2026) — [arXiv:2509.11523](https://arxiv.org/abs/2509.11523)
