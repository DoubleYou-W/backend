import os
import shutil
from uuid import uuid4
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHROMA_DIR = os.getenv("CHROMA_DIR", "./databases/chroma_db")
COLLECTION_NAME = "data"

embedding_fn = OllamaEmbeddings(model="all-minilm")

vectordb = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_fn,
    persist_directory=CHROMA_DIR,
    collection_metadata={"hnsw:space": "cosine"}
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    add_start_index=True
)

def add_to_vector_db(text: str, metadata: dict):
    chunks = splitter.split_text(text)

    if not chunks:
        raise ValueError("No chunks were produced from input text")

    ids = [str(uuid4()) for _ in chunks]
    metadatas = [metadata for _ in chunks]

    vectordb.add_texts(texts=chunks, ids=ids, metadatas=metadatas)

def get_relevant_docs(query: str, k: int = 5):
    results = vectordb.similarity_search_with_score(query, k=k)

    docs = [doc for doc, _ in results]
    return docs

def delete_vector_db():
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)