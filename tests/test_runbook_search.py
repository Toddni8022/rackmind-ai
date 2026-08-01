from services.vector_service import RunbookCollection


def _collection(tmp_path, files=None):
    runbook_dir = tmp_path / "runbooks"
    runbook_dir.mkdir()

    for name, text in (files or {}).items():
        (runbook_dir / f"{name}.txt").write_text(text, encoding="utf-8")

    return RunbookCollection(directories=[runbook_dir])


def test_search_ranks_best_match_first(tmp_path):
    collection = _collection(
        tmp_path,
        {
            "cooling": "CRAC unit failure. High temperature response steps.",
            "network": "CRC errors on switch uplinks. Replace optics.",
        },
    )

    results = collection.search("CRC errors on the switch")
    assert len(results) == 1
    assert "Replace optics" in results[0]


def test_search_returns_empty_when_nothing_matches(tmp_path):
    collection = _collection(tmp_path, {"cooling": "CRAC unit failure."})
    assert collection.search("kubernetes ingress rollback") == []


def test_search_ignores_short_stopwords(tmp_path):
    collection = _collection(tmp_path, {"cooling": "on to a is at"})
    assert collection.search("on to a") == []


def test_memory_docs_add_delete_and_count(tmp_path):
    collection = _collection(tmp_path)
    assert collection.count() == 0

    collection.add(ids=["fans"], documents=["Fan tray replacement procedure."])
    assert collection.count() == 1
    assert "Fan tray" in collection.search("fan replacement")[0]

    collection.delete(ids=["fans"])
    assert collection.count() == 0


def test_missing_directory_is_not_an_error(tmp_path):
    collection = RunbookCollection(directories=[tmp_path / "does-not-exist"])
    assert collection.count() == 0
    assert collection.search("anything") == []


def test_chroma_style_query_wrapper(tmp_path):
    collection = _collection(tmp_path, {"power": "UPS bypass procedure."})
    result = collection.query(query_texts=["UPS bypass"], n_results=2)
    assert result == {"documents": [["UPS bypass procedure."]]}
