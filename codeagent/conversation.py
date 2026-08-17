import json
import re

from prompts import QA_CHECKER_SYSTEM, assistant_system


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


def qa_check(llm, question, answer):
    """QA-Checker: is the answer on-topic? If not, produce a redirecting instruction."""
    res = llm.generate([
        {"role": "system", "content": QA_CHECKER_SYSTEM},
        {"role": "user", "content": f"Original question:\n{question}\n\nAnswer:\n{answer}"},
    ])
    return _parse_json(res)


def converse(llm, instructor, assistant, task, context, max_turns=3):
    """One atomic conversation: the instructor asks, the assistant answers,
    and the QA-Checker supervises for on-topicness until satisfied."""
    question = f"{instructor} asks you:\n{task}\n\nContext:\n{context}"
    messages = [
        {"role": "system", "content": assistant_system(assistant, instructor)},
        {"role": "user", "content": question},
    ]

    for turn in range(max_turns):
        answer = llm.generate(messages)
        messages.append({"role": "assistant", "content": answer})

        verdict = qa_check(llm, question, answer)
        if verdict.get("relevant", False):
            return answer

        instruction = verdict.get("instruction", "Re-read the original question and answer it directly.")
        print(f"  [QA-Checker] off-topic, re-asking: {instruction}")
        messages.append({
            "role": "user",
            "content": f"QA-Checker: {instruction} Re-read the original question and answer again.",
        })

    return answer