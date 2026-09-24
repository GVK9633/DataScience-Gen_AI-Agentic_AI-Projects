
query_cache = {}
context_cache = {}

def get_cached_answer(query):
    return query_cache.get(query)

def set_cached_answer(query, answer):
    query_cache[query] = answer
