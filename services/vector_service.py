"""
RackMind AI

Vector Runbook Search Service

Uses TF-IDF document vectors and cosine similarity for real
vector-space retrieval, without requiring an embeddings API or
ChromaDB, so the Streamlit Cloud deployment stays free of heavy
runtime dependencies.
"""

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

RUNBOOK_DIRS = (
    Path("sample_data/runbooks"),
    Path("data/runbooks"),
)


class RunbookCollection:
    """
    TF-IDF vector search collection over runbook text files plus any
    documents indexed at runtime.
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
        """Return the text of the best-matching runbooks by TF-IDF cosine similarity."""

        docs = self.load_all()

        if not docs or not query.strip():
            return []

        titles = list(docs.keys())
        corpus = [f"{title}\n{docs[title]}" for title in titles]

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            doc_vectors = vectorizer.fit_transform(corpus)
            query_vector = vectorizer.transform([query])
        except ValueError:
            # The corpus or query produced an empty vocabulary
            # (e.g. every token was a stopword).
            return []

        # TfidfVectorizer L2-normalizes each row by default, so the
        # dot product of the query against each document is exactly
        # its cosine similarity -- no separate similarity metric needed.
        scores = (doc_vectors @ query_vector.T).toarray().ravel()

        ranked = sorted(
            ((score, title) for score, title in zip(scores, titles) if score > 0),
            key=lambda item: item[0],
            reverse=True,
        )

        return [docs[title] for _, title in ranked[:limit]]

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
