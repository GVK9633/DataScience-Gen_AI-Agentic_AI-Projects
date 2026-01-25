
import asyncio
from cache import *
from router import classify_query
from retriever import retrieve_parallel
from reranker import rerank
from compressor import compress_context
from prompt import prompt
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

async def run_rag(query, vector_store):
    cached = get_cached_answer(query)
    if cached:
        return cached

    docs = await retrieve_parallel(vector_store, query)
    top_docs = rerank(query, docs)
    context = compress_context(top_docs)

    final_prompt = prompt.format(context=context, question=query)
    answer = llm.predict(final_prompt)
    set_cached_answer(query, answer)
    return answer
