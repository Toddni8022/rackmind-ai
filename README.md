# RackMind AI

## Autonomous Data Center Operations Copilot

RackMind AI is an AI-powered operations assistant for modern data centers. It combines Google ADK, Gemini, Retrieval-Augmented Generation (RAG), infrastructure logs, sensor telemetry, and operational runbooks to help investigate incidents and produce clear executive-level reports.

The project is built as a portfolio-ready AI agent demo focused on real data center problems: CRC errors, switch resets, heat events, environmental telemetry, runbook lookup, and incident response.

---

## What It Does

RackMind AI helps a data center operator answer questions like:

- Why are CRC errors increasing on this switch?
- Is the rack overheating?
- Do the logs and sensor readings point to the same issue?
- What runbook steps apply to this incident?
- What should be escalated first?
- How would this look in an executive incident report?

---

## Key Features

- Multi-agent architecture using Google ADK
- Gemini-powered incident analysis
- Coordinator agent for routing operational questions
- Log agent for switch and infrastructure events
- Sensor agent for temperature, humidity, and power telemetry
- Runbook agent using RAG-style retrieval
- Single-prompt incident investigation workflow
- Executive incident report generation
- Streamlit dashboard interface
- Dark themed UI configuration
- Structured parsers for logs and sensor CSV data

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
      |       - Parses infrastructure logs
      |       - Detects warnings, errors, CRC events, and resets
      |
      +--> Sensor Agent
      |       - Reviews rack temperature, humidity, and power data
      |       - Flags environmental risk
      |
      +--> Runbook Agent
      |       - Searches operational documentation
      |       - Returns relevant response steps
      |
      +--> Incident Investigation Tool
              - Combines logs, sensors, and runbooks
              - Generates an executive report
```

---

## Tech Stack

- Python
- Streamlit
- Google Gemini
- Google ADK
- Pandas
- ChromaDB / vector search concepts
- RAG-style runbook retrieval
- GitHub

---

## Project Structure

```text
rackmind-ai/
  adk/
    root_agent.py          # Google ADK coordinator agent
    tools.py               # ADK tool wrappers
    incident_tool.py       # Complete incident investigation workflow
    adk_service.py         # ADK runner service for the app
    test_adk.py            # ADK test runner

  agents/
    log_agent.py           # Log analysis agent
    sensor_agent.py        # Sensor analysis agent
    runbook_agent.py       # Runbook Q&A agent
    report_agent.py        # Incident report generation

  services/
    gemini_service.py      # Gemini API service
    log_parser.py          # Infrastructure log parser
    sensor_parser.py       # Sensor CSV parser
    vector_service.py      # Runbook search service
    incident_service.py    # Incident coordination service
    logger.py              # App logging

  data/
    sample logs, sensor data, and runbook material

  .streamlit/
    config.toml            # Dark theme UI settings
```

---

## Current Release

### RackMind AI v1.0.0

Completed:

- Multi-page Streamlit UI
- Coordinator agent
- Log agent
- Runbook agent
- Sensor analytics
- Executive report agent
- Google ADK root agent
- ADK tools
- Single-prompt incident investigation workflow
- Dark Streamlit theme
- Cleaner project structure
- Updated `.gitignore`

---

## Example Incident Workflow

1. Upload or load infrastructure log data.
2. Upload or load rack sensor CSV data.
3. RackMind parses the logs and telemetry.
4. The runbook agent retrieves relevant operational guidance.
5. The incident tool combines everything into one investigation.
6. Gemini generates an executive incident report with:
   - Executive summary
   - Root cause
   - Business impact
   - Recommended actions
   - Priority
   - Confidence level

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

Create a `.env` file if your local setup requires API keys:

```text
GOOGLE_API_KEY=your_api_key_here
```

Run the Streamlit app:

```bash
streamlit run main.py
```

If your local entry file has a different name, run Streamlit against that file instead.

---

## ADK Test Runner

To test the Google ADK agent flow directly:

```bash
python adk/test_adk.py
```

The test runner sends a sample question about CRC errors to the RackMind coordinator agent.

---

## Roadmap

Planned improvements:

- PDF incident export
- Historical incident search
- Authentication
- Live infrastructure dashboard
- Multi-rack monitoring
- Trend analytics
- Hugging Face or cloud deployment
- Demo video
- Architecture diagram
- Kaggle capstone polish

---

## Why This Project Matters

Data centers generate a lot of operational noise: logs, sensor readings, alerts, runbooks, and escalation notes. RackMind AI demonstrates how an AI operations copilot can reduce that noise into a clear investigation path.

Instead of only showing a chatbot, this project shows a practical AI workflow tied to real infrastructure work:

- Detect the issue
- Pull supporting evidence
- Compare telemetry against logs
- Search operational guidance
- Generate an actionable report

---

## Status

RackMind AI is an active portfolio project and AI agent capstone demo.
