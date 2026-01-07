
def decision_agent(state):
    if state["policy_result"]["eligible"]:
        return {
            "decision": {
                "approved": True,
                "refund_amount": 45000
            }
        }
    return {
        "decision": {
            "approved": False,
            "reason": "Policy violation"
        }
    }
