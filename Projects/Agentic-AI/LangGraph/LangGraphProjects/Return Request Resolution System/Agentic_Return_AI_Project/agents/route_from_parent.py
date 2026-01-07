def route_from_parent(state):
    if "return" in state["input"].lower():
        return "policy_agent"
    return "communication_agent"
