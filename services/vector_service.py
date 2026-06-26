"""
RackMind AI

Lightweight Runbook Search Service

This version avoids ChromaDB so the Streamlit Cloud deployment
stays compatible with the hosted Python runtime.
"""

from pathlib import Path

RUNBOOK_DIRS = [
    Path("sample_data/runbooks"),
    Path("data/runbooks"),
]


class RunbookCollection:
    """
    Small compatibility wrapper used by the dashboard.
    It provides count(), add_runbook(), and simple keyword search.
    """

    def __init__(self):
        self._memory_docs = {}

    def _load_files(self):
        docs = {}

        for directory in RUNBOOK_DIRS:
            if not directory.exists():
                continue

            for path in directory.glob("*.txt"):
                docs[path.stem] = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

        docs.update(self._memory_docs)
        return docs

    def count(self):
        return len(self._load_files())

    def add(self, ids, documents):
        for doc_id, document in zip(ids, documents):
            self._memory_docs[doc_id] = document

    def delete(self, ids):
        for doc_id in ids:
            self._memory_docs.pop(doc_id, None)

    def query(self, query_texts, n_results=3):
        query = query_texts[0] if query_texts else ""
        documents = search_runbooks(query, limit=n_results)
        return {"documents": [documents]}


collection = RunbookCollection()


def add_runbook(title: str, text: str):
    collection.add(
        ids=[title],
        documents=[text],
    )


def search_runbooks(query: str, limit: int = 3):
    docs = collection._load_files()

    if not docs:
        return []

    query_terms = {
        term.lower()
        for term in query.split()
        if len(term) > 2
    }

    scored = []

    for title, text in docs.items():
        searchable = f"{title}\n{text}".lower()
        score = sum(
            1 for term in query_terms
            if term in searchable
        )
        scored.append((score, title, text))

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        text for score, title, text in scored[:limit]
        if score > 0
    ] or [text for score, title, text in scored[:limit]]
