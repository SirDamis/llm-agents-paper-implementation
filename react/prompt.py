def build_system_prompt(tools):
    tool_lines = "\n".join(
        f"- {name}: {tool.description}" for name, tool in tools.items()
    )
    tool_names = ", ".join(tools.keys())
    return f"""You are an agent that answers questions by reasoning and acting step by step.

You can use the following tools:
{tool_lines}

Use the following format:

Thought: reason about what to do next
Action: the tool to use, must be one of [{tool_names}]
Action Input: the input to the tool
Observation: the result of the tool
... (Thought/Action/Action Input/Observation can repeat)

When you have the answer, end with:
Final Answer: the final answer to the question

If you cannot answer with the available tools, output:
Final Answer: I cannot answer this question."""
