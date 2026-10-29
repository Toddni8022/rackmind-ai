"""Invoke RackMind MCP tools with uploaded incident data over stdio."""
import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def _analyze(log_text: str, sensor_csv: str) -> tuple[dict, dict]:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "rackmind_mcp.server"],
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            results = []
            for name, arguments in (
                ("analyze_network_logs", {"log_text": log_text}),
                ("analyze_rack_sensors", {"sensor_csv": sensor_csv}),
            ):
                response = await session.call_tool(name, arguments)
                if response.isError:
                    raise RuntimeError(f"MCP tool {name} failed: {response.content}")
                blocks = [part.text for part in response.content if hasattr(part, "text")]
                if not blocks:
                    raise RuntimeError(f"MCP tool {name} returned no text")
                data = json.loads(blocks[0])
                if "summary" not in data:
                    raise RuntimeError(f"MCP tool {name} returned no summary: {data}")
                results.append(data)
            return results[0], results[1]

def analyze_incident(log_text: str, sensor_csv: str) -> tuple[dict, dict]:
    """Synchronous entrypoint for RackMind's incident investigation."""
    return asyncio.run(_analyze(log_text, sensor_csv))
