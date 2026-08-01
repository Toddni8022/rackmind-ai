"""
RackMind AI

Lightweight Runbook Search Service

This version avoids ChromaDB so the Streamlit Cloud deployment
stays compatible with the hosted Python runtime.
"""

from pathlib import Path

RUNBOOK_DIRS = (
    Path("sample_data/runbooks"),
    Path("data/runbooks"),
)

# Query terms this short ("a", "on", "to") match almost anything.
MIN_TERM_LENGTH = 3


class RunbookCollection:
    """
    Small keyword-search collection over runbook text files
    plus any documents indexed at runtime.
    """

    def __init__(self, directories=RUNBOOK_DIRS):
        self._directories = tuple(directories)
        self._memory_docs = {}

    def load_all(self) -> dict[str, str]:
        """Return {title: text} for every runbook on disk and in memory."""
        docs = {}

        for directory in self._directories:
            if not directory.exists():
                continue

            for path in sorted(directory.glob("*.txt")):
                docs[path.stem] = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

        docs.update(self._memory_docs)
        return docs

    def count(self) -> int:
        return len(self.load_all())

    def add(self, ids, documents):
        for doc_id, document in zip(ids, documents):
            self._memory_docs[doc_id] = document

    def delete(self, ids):
        for doc_id in ids:
            self._memory_docs.pop(doc_id, None)

    def search(self, query: str, limit: int = 3) -> list[str]:
        """Return the text of the best-matching runbooks, if any match."""
        docs = self.load_all()

        if not docs:
            return []

        query_terms = {
            term.lower()
            for term in query.split()
            if len(term) >= MIN_TERM_LENGTH
        }

        scored = []

        for title, text in docs.items():
            searchable = f"{title}\n{text}".lower()
            score = sum(1 for term in query_terms if term in searchable)

            if score > 0:
                scored.append((score, title, text))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [text for _, _, text in scored[:limit]]

    def query(self, query_texts, n_results=3):
        """ChromaDB-style compatibility wrapper."""
        query = query_texts[0] if query_texts else ""
        documents = self.search(query, limit=n_results)
        return {"documents": [documents]}


collection = RunbookCollection()


def add_runbook(title: str, text: str):
    collection.add(
        ids=[title],
        documents=[text],
    )


def search_runbooks(query: str, limit: int = 3) -> list[str]:
    return collection.search(query, limit=limit)
