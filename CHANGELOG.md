# Changelog

## v0.9

### Added

- Anthropic Claude as a third AI provider (`AI_PROVIDER=claude`), with the
  same key-mismatch detection and graceful degradation as Gemini and OpenAI
- Historical Incident Search tab over past resolved incidents
- PDF export on the Log Agent and Sensor Agent tabs (previously only on
  Incident Commander)
- Upload size guard (`MAX_UPLOAD_MB`, default 20 MB) with a friendly
  rejection message instead of stalling on oversized files
- Test coverage for the AI-dependent agents (runbook Q&A, executive
  report generation, single-prompt incident investigation) via a mocked
  AI client

### Changed

- Runbook search now uses TF-IDF vectors and cosine similarity instead of
  naive keyword-presence counting, so ranking reflects real topical
  relevance rather than raw term overlap
- The three AI providers' retry/backoff/error-formatting logic is now a
  single shared helper instead of three near-duplicate implementations

## v0.8

### Added

- Google ADK root agent with incident investigation tool
- PDF incident export (in-memory, markup-safe)
- OpenAI support with automatic provider selection
- Topology view wired into the main dashboard tabs
- Ruff linting and expanded offline test suite in CI

### Changed

- One hardened log parser shared by every view and agent
- Runbook search returns only genuinely matching documents
- Streamlit views moved from `pages/` to `views/` so Streamlit
  no longer auto-registers broken sidebar pages

### Removed

- Unused agents, empty placeholder modules, and dead dependencies
  (pypdf, graphviz)

## v0.7

### Added

- Multi-page Streamlit UI
- Log Agent
- Runbook Agent
- Sensor Analytics
- Coordinator Agent
- Report Agent
