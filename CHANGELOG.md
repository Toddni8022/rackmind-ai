# Changelog

## v1.1

### Added

- Historical incident search: SQLite archive with filters for rack, severity, time range, root cause, recommended fix, and full-text search, plus CSV export. Incident Commander reports are archived automatically.
- Live telemetry connectors: Prometheus, Redfish, SNMP, syslog, AWS CloudWatch, and a built-in simulator, all returning one normalized reading shape and failing with clear operator-facing messages.
- Authentication + roles: login with operator / manager / admin roles, PBKDF2 password hashing, bootstrap admin account, and an admin user-management tab.
- Trend + prediction dashboard: temperature, power, CRC errors, resets, and health score over time per rack, with least-squares projections flagging racks likely to go critical within 24 hours.
- Test suite: 125 pytest tests covering log parsing, sensor parsing, scoring thresholds, report generation, AI fallback behavior, the incident archive, auth, trends, and connectors.
- Centralized health scoring service shared by the log page and trend dashboard.

### Changed

- Main app now gates tabs behind login when authentication is enabled (RACKMIND_AUTH=off restores open access).
- Streamlit auto sidebar navigation disabled so auth-gated tabs stay gated.

### Fixed

- Log severity is now read from the log's level token (ERROR/WARNING/CRIT/...), so "WARNING CRC error detected" lines are no longer double-counted as both warnings and errors.
- Interface reset counts no longer include "reset complete" recovery messages.
- Executive report prompts are grounded: empty log/sensor/runbook sections are marked NOT PROVIDED and the model is instructed not to invent metrics, ports, sensor readings, or runbook titles, and not to rule out causes the data supports.

## v0.7

### Added

- Multi-page Streamlit UI
- Log Agent
- Runbook Agent
- Sensor Analytics
- Coordinator Agent
- Report Agent

### Planned

- Google ADK Agent Tools
- MCP Server
- ChromaDB
- PDF Export
