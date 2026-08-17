import json
import re

from prompts import (
    ANALYZER_ROLES,
    META_SYSTEM,
    aggregator_system,
    analyzer_system,
    assumption_pruner_system,
    final_validator_system,
    trigger_planner_system,
)

BASE_ANALYZERS = ["static_analyzer", "behavior_analyzer", "memory_layout"]


def _parse_json(text):
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}


def _chat(llm, system, user):
    return llm.generate([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])


def run_pipeline(llm, code):
    # --- Phase 1: multi-view detection ---
    print("--- Phase 1: multi-view detection ---")
    meta = _parse_json(_chat(llm, META_SYSTEM, code))
    activated = [a for a in meta.get("activate", []) if a in ANALYZER_ROLES]
    agents = BASE_ANALYZERS + activated
    print(f"Activated analyzers: {', '.join(agents)}")

    reports = {}
    for name in agents:
        role, cwes = ANALYZER_ROLES[name]
        print(f"\n[{name}]")
        data = _parse_json(_chat(llm, analyzer_system(name, role, cwes), code))
        findings = data.get("findings", [])
        print(json.dumps(findings, indent=2))
        reports[name] = findings

    # --- Phase 2: aggregation ---
    print("\n--- Phase 2: aggregation ---")
    agg_input = json.dumps(reports, indent=2) + "\n\nCode:\n" + code
    candidates = _parse_json(_chat(llm, aggregator_system(), agg_input)).get("confirmed_issues", [])
    print(json.dumps(candidates, indent=2))
    if not candidates:
        return {"vulnerability_reported": False, "cwe_list": [], "report": "No candidates found."}

    # --- Phase 3: hypothesis construction ---
    print("\n--- Phase 3: hypothesis construction ---")
    tp_input = json.dumps(candidates, indent=2) + "\n\nCode:\n" + code
    hypotheses = _parse_json(_chat(llm, trigger_planner_system(), tp_input)).get("hypotheses", [])
    print(json.dumps(hypotheses, indent=2))
    if not hypotheses:
        return {"vulnerability_reported": False, "cwe_list": [], "report": "No hypotheses constructed."}

    # --- Phase 4: hypothesis-conditions validation ---
    print("\n--- Phase 4: hypothesis-conditions validation ---")
    retained = []
    for h in hypotheses:
        print(f"\n[candidate {h.get('cwe')} @ {h.get('sink_lines')}]")
        ap_input = json.dumps(h, indent=2) + "\n\nCode context:\n" + code
        verdicts = _parse_json(_chat(llm, assumption_pruner_system(), ap_input))
        print(json.dumps(verdicts, indent=2))
        if verdicts.get("hypothesis_retained", True):
            h["condition_verdicts"] = verdicts.get("verdicts", [])
            retained.append(h)

    if not retained:
        return {"vulnerability_reported": False, "cwe_list": [], "report": "All hypotheses pruned."}

    # --- Phase 5: hypothesis-path verification ---
    print("\n--- Phase 5: hypothesis-path verification ---")
    fv_input = json.dumps(retained, indent=2) + "\n\nCode context:\n" + code
    verdict = _parse_json(_chat(llm, final_validator_system(), fv_input))
    print(json.dumps(verdict, indent=2))
    return verdict
