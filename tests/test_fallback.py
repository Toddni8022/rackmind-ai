"""
Tests for AI-provider fallback behavior: the app must degrade to
clear operator-facing messages when no API keys are configured,
never crash.
"""

import services.gemini_service as gemini_service
from services.gemini_service import AIService


class TestProviderSelection:

    def _service(self):
        return AIService()

    def test_auto_prefers_openai_when_key_present(self, monkeypatch):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "auto")
        monkeypatch.setattr(gemini_service, "OPENAI_API_KEY", "sk-test")
        monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", "AIza-test")

        assert self._service()._provider() == "openai"

    def test_auto_falls_back_to_gemini(self, monkeypatch):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "auto")
        monkeypatch.setattr(gemini_service, "OPENAI_API_KEY", None)
        monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", "AIza-test")

        assert self._service()._provider() == "gemini"

    def test_auto_defaults_to_gemini_with_no_keys(self, monkeypatch):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "auto")
        monkeypatch.setattr(gemini_service, "OPENAI_API_KEY", None)
        monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", None)

        assert self._service()._provider() == "gemini"

    def test_explicit_provider_names(self, monkeypatch):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "google")
        assert self._service()._provider() == "gemini"

        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "gpt")
        assert self._service()._provider() == "openai"


class TestMissingKeyFallback:

    def test_gemini_without_key_returns_message_not_exception(
        self, monkeypatch
    ):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", None)

        result = AIService().generate("hello")

        assert "AI Service Not Configured" in result

    def test_openai_without_key_returns_message_not_exception(
        self, monkeypatch
    ):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "openai")
        monkeypatch.setattr(gemini_service, "OPENAI_API_KEY", None)

        result = AIService().generate("hello")

        assert "AI Service Not Configured" in result

    def test_mismatched_gemini_key_is_detected(self, monkeypatch):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", "sk-oops")

        result = AIService().generate("hello")

        assert "looks like an OpenAI key" in result

    def test_mismatched_openai_key_is_detected(self, monkeypatch):
        monkeypatch.setattr(gemini_service, "AI_PROVIDER", "openai")
        monkeypatch.setattr(gemini_service, "OPENAI_API_KEY", "AIza-oops")

        result = AIService().generate("hello")

        assert "looks like a Google Gemini key" in result


class TestRunbookFallback:

    def test_search_returns_empty_list_when_no_runbooks(
        self, tmp_path, monkeypatch
    ):
        import services.vector_service as vector_service

        monkeypatch.setattr(
            vector_service,
            "RUNBOOK_DIRS",
            [tmp_path / "missing"],
        )

        collection = vector_service.RunbookCollection()

        assert collection.count() == 0
        assert vector_service.search_runbooks("overheating") == []

    def test_in_memory_runbooks_are_searchable(self, tmp_path, monkeypatch):
        import services.vector_service as vector_service

        monkeypatch.setattr(
            vector_service,
            "RUNBOOK_DIRS",
            [tmp_path / "missing"],
        )

        collection = vector_service.RunbookCollection()
        monkeypatch.setattr(vector_service, "collection", collection)

        collection.add(
            ids=["cooling"],
            documents=["Check CRAC units when racks overheat."],
        )

        results = vector_service.search_runbooks("overheat racks")

        assert results
        assert "CRAC" in results[0]
