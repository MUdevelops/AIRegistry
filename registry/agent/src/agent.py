"""Minimal tool-calling loop. `plan` returns (tool, arg) or None to stop."""
TOOLS = {"echo": lambda x: x, "upper": str.upper}


def plan(goal, steps):
    return ("upper", goal) if not steps else None


def run(goal, tools=TOOLS, plan=plan, max_steps=5):
    steps = []
    for _ in range(max_steps):
        call = plan(goal, steps)
        if call is None:
            break
        name, arg = call
        steps.append((name, tools[name](arg)))
    return steps
