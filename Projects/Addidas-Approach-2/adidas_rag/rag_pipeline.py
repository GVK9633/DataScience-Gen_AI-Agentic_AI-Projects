import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

def load_csv_as_documents(csv_path: str):
    df = pd.read_csv(csv_path)

    documents = []
    for idx, row in df.iterrows():
        text = " | ".join([f"{col}: {str(row[col])}" for col in df.columns])

        doc = Document(
            page_content=text,
            metadata={col: row[col] for col in df.columns}
        )
        documents.append(doc)

    return documents


def build_vector_db(documents, persist_dir="db/adidas_products"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectordb


def load_or_create_db(csv_file, persistent_dir):
    if os.path.exists(persistent_dir):
        vectordb = Chroma(
            persist_directory=persistent_dir,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
    else:
        documents = load_csv_as_documents(csv_file)
        vectordb = build_vector_db(documents, persist_dir=persistent_dir)
    return vectordb


def search_db(query, vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    return retriever.invoke(query)