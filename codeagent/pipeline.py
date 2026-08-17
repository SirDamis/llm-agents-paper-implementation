from conversation import converse


def run_pipeline(llm, diff, commit_message):
    review_input = f"Commit message:\n{commit_message}\n\nDiff:\n{diff}"

    # --- Phase 1: Basic Info Sync ---
    print("--- Phase 1: Basic Info Sync (CEO, CTO, Coder) ---")
    info = converse(
        llm, "CEO", "Coder",
        "Identify the programming language of the change and the kind of change it is (modality).",
        review_input,
    )
    print(info)

    # --- Phase 2: Code Review (CA, VA, FA) ---
    print("\n--- Phase 2: Code Review (Coder, Reviewer) ---")
    ca = converse(
        llm, "Reviewer", "Coder",
        "Consistency analysis (CA): does the commit message accurately describe what the code change does?",
        review_input,
    )
    print(f"\n[CA]\n{ca}")

    va = converse(
        llm, "Reviewer", "Coder",
        "Vulnerability analysis (VA): does this code change introduce a vulnerability?",
        review_input,
    )
    print(f"\n[VA]\n{va}")

    fa = converse(
        llm, "Reviewer", "Coder",
        "Format analysis (FA): does the code change follow the surrounding project's formatting and style?",
        review_input,
    )
    print(f"\n[FA]\n{fa}")

    # --- Phase 3: Code Alignment (CR) ---
    print("\n--- Phase 3: Code Alignment (Coder, Reviewer) ---")
    report = (
        f"{review_input}\n\nReview findings:\n"
        f"CA: {ca}\nVA: {va}\nFA: {fa}"
    )
    revision = converse(
        llm, "Reviewer", "Coder",
        "Suggest a revised version of the code that addresses the findings above.",
        report,
    )
    print(f"\n[Revision]\n{revision}")

    # --- Phase 4: Document ---
    print("\n--- Phase 4: Document (CEO, CPO, Coder, Reviewer) ---")
    final = converse(
        llm, "CEO", "CPO",
        "Synthesize the final code review comments for all stakeholders, covering consistency, vulnerabilities, format, and the proposed revision.",
        f"{report}\nProposed revision:\n{revision}",
    )
    print(f"\n[Final comments]\n{final}")

    return {
        "info_sync": info,
        "ca": ca,
        "va": va,
        "fa": fa,
        "revision": revision,
        "final_comments": final,
    }