
import asyncio

async def vector_search(vs, query):
    return vs.similarity_search(query, k=8)

async def retrieve_parallel(vs, query):
    task = asyncio.create_task(vector_search(vs, query))
    results = await asyncio.gather(task)
    return results[0]
