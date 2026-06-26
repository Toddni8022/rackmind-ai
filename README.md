# RackMind AI

## Data Center Operations Copilot

RackMind AI is a Streamlit-based AI operations assistant for data center incident review. It analyzes switch logs, rack sensor telemetry, and runbook guidance, then uses Google Gemini to produce a clear executive-style incident report.

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
- Google Gemini incident report generation
- Coordinator agent that routes work to specialized agents
- Log agent for switch warnings, errors, CRC events, resets, and temperatures
- Sensor agent for temperature, humidity, and power telemetry
- Runbook search workflow
- Defensive parsing so missing CSV fields do not crash the app
- Clear fallback messages when Gemini is not configured

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
              - Uses Gemini to generate an executive report
```

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Google Gemini
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
    report_agent.py        # Gemini incident report agent

  pages/
    dashboard.py           # Dashboard tab
    logs.py                # Log analysis tab
    sensors.py             # Sensor analytics tab
    runbook.py             # Runbook search tab
    incident.py            # Incident commander tab
    topology.py            # Topology view

  services/
    gemini_service.py      # Central Gemini service
    log_parser.py          # Log parser
    sensor_parser.py       # Sensor CSV parser
    vector_service.py      # Runbook search service
    incident_service.py    # Incident coordination service
    logger.py              # App logging

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

Create a local `.env` file:

```text
GOOGLE_API_KEY=your_google_ai_studio_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Run the app:

```bash
streamlit run rackmind.py
```

---

## Streamlit Cloud Deployment

For Streamlit Community Cloud, use:

```text
Repository: Toddni8022/rackmind-ai
Branch: main
Main file path: rackmind.py
```

Add these secrets in Streamlit Cloud:

```toml
GOOGLE_API_KEY = "your_google_ai_studio_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
```

A valid Gemini key usually starts with `AIza`. If the key starts with `sk-`, it is likely an OpenAI key and will not work with this Gemini app.

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
5. Gemini generates an executive incident report with:
   - Executive summary
   - Root cause
   - Business impact
   - Recommended actions
   - Priority
   - Confidence level

---

## Roadmap

- PDF incident export
- Historical incident search
- Authentication
- Live infrastructure dashboard
- Multi-rack monitoring
- Trend analytics
- Demo video
- Architecture diagram
- Kaggle capstone polish

---

## Status

RackMind AI is an active AI agent capstone and portfolio project focused on practical data center operations.
