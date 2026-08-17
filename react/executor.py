def execute(action, action_input, tools):
    tool = tools.get(action)
    if tool is None:
        return f"Error: unknown tool '{action}'. Available tools: {', '.join(tools)}"
    try:
        return tool.run(action_input or "")
    except Exception as e:
        return f"Error executing {action}: {e}"
