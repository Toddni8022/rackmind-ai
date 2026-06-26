"""
RackMind AI

Vector Service
"""

import chromadb

client = chromadb.PersistentClient(path="data/chroma")

collection = client.get_or_create_collection(
    name="runbooks"
)


def add_runbook(title: str, text: str):

    # Delete old version if it exists
    try:
        collection.delete(ids=[title])
    except Exception:
        pass

    collection.add(
        ids=[title],
        documents=[text],
    )


def search_runbooks(query: str, limit: int = 3):

    results = collection.query(
        query_texts=[query],
        n_results=limit,
    )

    docs = results.get("documents")

    if not docs:
        return []

    return docs[0]