
def compress_context(docs):
    return "\n".join(d.page_content[:300] for d in docs)
