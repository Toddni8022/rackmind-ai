"""RackMind read-only MCP server for synthetic data center telemetry."""
from pathlib import Path
import json
import pandas as pd
from mcp.server.fastmcp import FastMCP
from services.log_parser import parse_log, build_log_timeline
from services.sensor_parser import parse_sensor_data
from agents.log_agent import analyze_log_summary
from agents.sensor_agent import analyze_sensor_data

mcp = FastMCP("RackMind")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

@mcp.tool()
def analyze_network_logs(log_text: str = "") -> str:
    """Analyze bundled sample switch logs for errors, CRC events and interface resets."""
    path = DATA_DIR / "switch.log"
    if not log_text and not path.is_file():
        return "Sample switch log not found."
    content = log_text if log_text else path.read_text(encoding="utf-8")
    summary = parse_log(content)
    return json.dumps({"source": "uploaded data" if log_text else "bundled sample data", "summary": summary,
                       "timeline": build_log_timeline(content),
                       "analysis": analyze_log_summary(summary)}, indent=2)

@mcp.tool()
def analyze_rack_sensors(sensor_csv: str = "") -> str:
    """Analyze bundled sample rack temperature, humidity and power telemetry."""
    path = DATA_DIR / "rack_temperature.csv"
    if not sensor_csv and not path.is_file():
        return "Sample rack sensor CSV not found."
    from io import StringIO
    summary = parse_sensor_data(pd.read_csv(StringIO(sensor_csv)) if sensor_csv else pd.read_csv(path))
    return json.dumps({"source": "uploaded data" if sensor_csv else "bundled sample data", "summary": summary,
                       "analysis": analyze_sensor_data(summary)}, indent=2)

if __name__ == "__main__":
    mcp.run()
