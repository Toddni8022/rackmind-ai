# Changelog

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
