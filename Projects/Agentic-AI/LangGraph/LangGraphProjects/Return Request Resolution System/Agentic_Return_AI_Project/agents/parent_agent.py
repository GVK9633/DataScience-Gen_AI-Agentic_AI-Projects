
def parent_agent(state):
    # if "return" in state["input"].lower():
    #     return "policy_agent"
    # return "communication_agent"
    # Node must return a dict
    return {
        "input": state["input"]
    }
    
    
