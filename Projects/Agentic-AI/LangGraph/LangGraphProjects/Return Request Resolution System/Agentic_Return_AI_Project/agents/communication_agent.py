
def communication_agent(state):
    decision = state.get("decision")
    if decision and decision.get("approved"):
        return {
            "response": f"Return approved. Refund ₹{decision['refund_amount']} will be processed."
        }
    return {
        "response": "Return request rejected based on policy."
    }
