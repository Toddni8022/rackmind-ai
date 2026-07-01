# RackMind AI

## Data Center Operations Copilot

RackMind AI is a Streamlit-based AI operations assistant for data center incident review. It analyzes switch logs, rack sensor telemetry, and runbook guidance, then uses either Google Gemini or OpenAI to produce a clear executive-style incident report.

This project is built around a real infrastructure workflow: CRC errors, interface resets, temperature events, rack power draw, runbook lookup, and escalation recommendations.

---

## What It Does

RackMind AI helps an operator answer questions like:

- Why are CRC errors increasing?
- Is the rack overheating?
- Are the logs and sensors pointing to the same problem?
- What runbook steps apply?
- What should be escalated first?
- How would this incident look in an executive report?

---

## Key Features

- Multi-page Streamlit dashboard
- Gemini or OpenAI incident report generation
- Provider selection with `AI_PROVIDER=auto`, `gemini`, or `openai`
- Coordinator agent that routes work to specialized agents
- Log agent for switch warnings, errors, CRC events, resets, and temperatures
- Sensor agent for temperature, humidity, and power telemetry
- Runbook search workflow
- **Historical incident search** — every generated report is archived and searchable by rack, severity, timestamp, root cause, and recommended fix
- **Live telemetry connectors** — pull data straight from Prometheus, Redfish BMCs, SNMP, syslog files, or AWS CloudWatch (plus a built-in simulator for demos)
- **Authentication + roles** — login with operator, manager, and admin roles for shared team deployments
- **Trend + prediction dashboard** — temperature, power, CRC errors, resets, and health score over time, with racks projected to go critical flagged early
- **Test suite** — 125 pytest tests covering log parsing, sensor parsing, scoring thresholds, report generation, fallback behavior, the incident archive, auth, trends, and connectors
- Defensive parsing so missing CSV fields do not crash the app
- Clear fallback messages when API keys are missing or mismatched

---

## Architecture

```text
User / Operator
      |
      v
Streamlit Dashboard
      |
      v
RackMind Coordinator Agent
      |
      +--> Log Agent
      |       - Parses switch and infrastructure logs
      |       - Detects warnings, errors, CRC events, resets, and heat events
      |
      +--> Sensor Agent
      |       - Reviews rack temperature, humidity, and power data
      |       - Flags environmental risk
      |
      +--> Runbook Agent
      |       - Searches operational documentation
      |       - Returns relevant response steps
      |
      +--> Report Agent
              - Combines logs, sensors, and runbooks
              - Uses Gemini or OpenAI to generate an executive report
```

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Google Gemini
- OpenAI
- Google ADK
- RAG-style runbook retrieval
- GitHub

---

## Project Structure

```text
rackmind-ai/
  rackmind.py              # Main Streamlit entry point

  agents/
    coordinator.py         # Routes work between agents
    log_agent.py           # Log analysis agent
    sensor_agent.py        # Sensor analysis agent
    runbook_agent.py       # Runbook Q&A agent
    report_agent.py        # Incident report agent

  pages/
    dashboard.py           # Dashboard tab
    logs.py                # Log analysis tab
    sensors.py             # Sensor analytics tab
    runbook.py             # Runbook search tab
    incident.py            # Incident commander tab
    telemetry.py           # Live telemetry connectors tab
    trends.py              # Trend + prediction dashboard tab
    history.py             # Historical incident search tab
    admin.py               # User administration tab (admin role)
    topology.py            # Topology view

  connectors/
    base.py                # Connector interface + normalized reading shape
    prometheus_connector.py# Prometheus HTTP API
    redfish_connector.py   # DMTF Redfish BMC thermal/power
    snmp_connector.py      # SNMP v2c polling (optional pysnmp)
    syslog_connector.py    # Syslog file tail
    cloudwatch_connector.py# AWS CloudWatch custom metrics (optional boto3)
    simulator.py           # Built-in demo telemetry generator

  services/
    gemini_service.py      # Central AI provider service
    log_parser.py          # Log parser
    sensor_parser.py       # Sensor CSV parser
    scoring.py             # Health score thresholds
    vector_service.py      # Runbook search service
    incident_service.py    # Incident coordination service
    incident_archive.py    # Historical incident archive (SQLite)
    telemetry_store.py     # Telemetry history (SQLite)
    trend_service.py       # Trend fitting + failure prediction
    auth_service.py        # Login + operator/manager/admin roles
    db.py                  # Shared SQLite helper
    logger.py              # App logging

  tests/                   # Pytest suite (parsing, scoring, reports,
                           # fallback, archive, auth, trends, connectors)

  data/                    # Sample logs, sensors, and runbooks
  .streamlit/              # Streamlit settings
```

---

## Setup

Clone the repository:

```bash
git clone https://github.com/Toddni8022/rackmind-ai.git
cd rackmind-ai
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file.

For automatic provider selection:

```text
AI_PROVIDER=auto
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-5.5
```

For Gemini only:

```text
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_google_ai_studio_key_here
GEMINI_MODEL=gemini-2.5-flash
```

For OpenAI only:

```text
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-5.5
```

Run the app:

```bash
streamlit run rackmind.py
```

Run the tests:

```bash
pytest tests/
```

---

## Authentication + Roles

RackMind ships with login support for shared team deployments. On
first run a default **admin / rackmind** account is created — sign in
and change the password immediately (the sidebar warns until you do).

| Role     | Access |
|----------|--------|
| operator | Dashboards, log/sensor analysis, live telemetry, trends, incident reports, history search |
| manager  | Everything operators can do, plus deleting archived incidents |
| admin    | Everything, plus user administration (add users, set roles, reset passwords) |

Environment options:

```text
RACKMIND_AUTH=on               # default; set to off for single-operator demos
RACKMIND_ADMIN_PASSWORD=...    # bootstrap admin password on first run
RACKMIND_DB=...                # override the SQLite database path
```

---

## Live Telemetry Connectors

The Live Telemetry tab pulls readings directly from real sources
instead of uploaded files. Fetched readings feed the same AI analysis
pipeline and are stored in telemetry history for the Trends dashboard.

| Connector  | Source | Notes |
|------------|--------|-------|
| Simulator  | Built-in generator | Works out of the box for demos |
| Prometheus | HTTP API instant queries | Configurable PromQL per metric |
| Redfish    | BMC thermal + power endpoints | iDRAC, iLO, XClarity, OpenBMC |
| SNMP       | v2c OID polling | Requires `pip install pysnmp` |
| Syslog     | File tail | Point rsyslog / syslog-ng at a file |
| CloudWatch | AWS custom metrics | Requires `pip install boto3` |

Connectors degrade gracefully: unreachable endpoints or missing
optional packages produce a clear operator-facing message, never a
crash.

---

## Historical Incident Search

Every report generated by the Incident Commander is saved to a SQLite
archive automatically. The History tab filters incidents by rack,
severity, time range, root cause, recommended fix, and full-report
text, with CSV export. Managers and admins can delete entries.

---

## Trend + Prediction Dashboard

The Trends tab charts temperature, power, CRC errors, interface
resets, and health score over time for every rack with telemetry
history. A least-squares trend is fitted per rack and any rack
projected to cross the critical temperature (90°F), power (4.5 kW),
or health score (<70) thresholds within 24 hours is flagged with an
estimated time to critical.

---

## Streamlit Cloud Deployment

For Streamlit Community Cloud, use:

```text
Repository: Toddni8022/rackmind-ai
Branch: main
Main file path: rackmind.py
```

Add one of these secret blocks in Streamlit Cloud.

OpenAI:

```toml
AI_PROVIDER = "openai"
OPENAI_API_KEY = "your_openai_key_here"
OPENAI_MODEL = "gpt-5.5"
```

Gemini:

```toml
AI_PROVIDER = "gemini"
GOOGLE_API_KEY = "your_google_ai_studio_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
```

Auto mode:

```toml
AI_PROVIDER = "auto"
OPENAI_API_KEY = "your_openai_key_here"
GOOGLE_API_KEY = "your_google_ai_studio_key_here"
OPENAI_MODEL = "gpt-5.5"
GEMINI_MODEL = "gemini-2.5-flash"
```

In auto mode, RackMind uses OpenAI when `OPENAI_API_KEY` is present. If no OpenAI key is present, it falls back to Gemini when a Google key is present.

A valid Gemini key usually starts with `AIza`. A valid OpenAI key usually starts with `sk-`.

---

## Sensor CSV Format

The sensor page works best with columns like:

```csv
timestamp,rack,temperature,humidity,power_kw
2026-06-26 08:00,Rack-22,78,45,3.9
2026-06-26 08:05,Rack-22,84,47,4.2
2026-06-26 08:10,Rack-22,91,49,4.8
```

The parser also accepts common variations such as `temp`, `temp_f`, `rack_temperature`, `relative_humidity`, `power`, and `load_kw`.

---

## Example Incident Workflow

1. Upload switch log data.
2. Upload rack sensor CSV data.
3. RackMind parses logs and telemetry.
4. The runbook workflow retrieves relevant guidance.
5. Gemini or OpenAI generates an executive incident report with:
   - Executive summary
   - Root cause
   - Business impact
   - Recommended actions
   - Priority
   - Confidence level

---

## Roadmap

- [x] PDF incident export
- [x] Historical incident search
- [x] Authentication + roles
- [x] Live telemetry connectors
- [x] Multi-rack monitoring
- [x] Trend analytics + failure prediction
- [x] Test suite
- [ ] Demo video
- [ ] Architecture diagram
- [ ] Kaggle capstone polish

---

## Status

RackMind AI is an active AI agent capstone and portfolio project focused on practical data center operations.
