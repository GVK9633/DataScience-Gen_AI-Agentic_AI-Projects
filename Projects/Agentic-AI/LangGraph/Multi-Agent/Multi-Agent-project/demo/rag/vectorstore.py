import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

VECTOR_DIR = "rag/vector_db"

def setup_vectorstore():
    os.makedirs(VECTOR_DIR, exist_ok=True)
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=VECTOR_DIR, embedding_function=embeddings)
    return vectordb
