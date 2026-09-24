
def classify_query(query: str):
    if len(query.split()) < 6:
        return "simple"
    if "compare" in query.lower():
        return "analytical"
    return "factual"
