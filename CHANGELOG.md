# Changelog

## v1.0.0

### Added

- Streamlit operations console for data center incident response.
- Synced Dashboard with latest log, sensor, and incident analyses.
- Deterministic health scoring and executive report fallback.
- Optional Gemini / Google ADK reporting layer.
- ChromaDB-backed runbook retrieval.
- PDF incident report export.
- Sample sensor and switch log data for demos.
- PowerShell launcher that uses the project virtual environment.

### Fixed

- Missing runtime dependencies for Plotly charts and PDF reports.
- Dashboard score flattening to `0/100` when one subsystem was critical.
- App startup failures caused by launching global Python instead of `.venv`.
- Generated runtime dashboard state leaking into git status.

### Submission Polish

- Completed README quick start and architecture notes.
- Added `.env.example`.
- Added sample log file for judge testing.
