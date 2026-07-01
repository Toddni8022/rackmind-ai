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
