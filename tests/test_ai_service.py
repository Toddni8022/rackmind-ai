import services.gemini_service as gemini_service
from services.gemini_service import AIService


def _service(monkeypatch, provider="auto", openai_key=None, anthropic_key=None, gemini_key=None):
    monkeypatch.setattr(gemini_service, "AI_PROVIDER", provider)
    monkeypatch.setattr(gemini_service, "OPENAI_API_KEY", openai_key)
    monkeypatch.setattr(gemini_service, "ANTHROPIC_API_KEY", anthropic_key)
    monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", gemini_key)
    return AIService()


def test_auto_prefers_openai_when_configured(monkeypatch):
    service = _service(monkeypatch, openai_key="sk-openai", anthropic_key="sk-ant-x", gemini_key="AIzaX")
    assert service._provider() == "openai"


def test_auto_falls_back_to_claude_when_no_openai_key(monkeypatch):
    service = _service(monkeypatch, anthropic_key="sk-ant-x", gemini_key="AIzaX")
    assert service._provider() == "claude"


def test_auto_falls_back_to_gemini_when_only_gemini_key(monkeypatch):
    service = _service(monkeypatch, gemini_key="AIzaX")
    assert service._provider() == "gemini"


def test_explicit_claude_provider_selected_regardless_of_keys(monkeypatch):
    service = _service(monkeypatch, provider="claude", openai_key="sk-openai")
    assert service._provider() == "claude"


def test_unknown_provider_raises(monkeypatch):
    service = _service(monkeypatch, provider="bogus")

    try:
        service._provider()
        assert False, "expected RuntimeError"
    except RuntimeError as ex:
        assert "claude" in str(ex)


def test_claude_client_rejects_openai_style_key(monkeypatch):
    service = _service(monkeypatch, provider="claude", anthropic_key="sk-not-anthropic")

    try:
        service._get_claude_client()
        assert False, "expected RuntimeError"
    except RuntimeError as ex:
        assert "OpenAI key" in str(ex)


def test_claude_client_rejects_gemini_style_key(monkeypatch):
    service = _service(monkeypatch, provider="claude", anthropic_key="AIzaSomeGeminiKey")

    try:
        service._get_claude_client()
        assert False, "expected RuntimeError"
    except RuntimeError as ex:
        assert "Gemini key" in str(ex)


def test_claude_client_requires_key(monkeypatch):
    service = _service(monkeypatch, provider="claude")

    try:
        service._get_claude_client()
        assert False, "expected RuntimeError"
    except RuntimeError as ex:
        assert "ANTHROPIC_API_KEY" in str(ex)
