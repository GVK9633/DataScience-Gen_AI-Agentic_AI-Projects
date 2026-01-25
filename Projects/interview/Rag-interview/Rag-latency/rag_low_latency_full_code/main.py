
import asyncio
from ingest import load_and_chunk
from vector_store import create_vector_store
from rag_pipeline import run_rag

docs = load_and_chunk("policy.txt")
vector_store = create_vector_store(docs)

query = "Compare ELSS and PPF tax benefits"
answer = asyncio.run(run_rag(query, vector_store))
print(answer)
