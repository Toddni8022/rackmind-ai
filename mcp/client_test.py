"""Smoke test: launch RackMind MCP over stdio, discover and call its tools.

Run from repository root: python -m mcp.client_test
"""
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    root = Path(__file__).resolve().parents[1]
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp.server"],
        cwd=str(root),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            available = await session.list_tools()
            names = {tool.name for tool in available.tools}
            expected = {"analyze_network_logs", "analyze_rack_sensors"}
            missing = expected - names
            if missing:
                raise RuntimeError(f"Missing MCP tools: {sorted(missing)}")
            print("Connected RackMind MCP tools:", ", ".join(sorted(names)))
            for name in sorted(expected):
                result = await session.call_tool(name, {})
                if result.isError:
                    raise RuntimeError(f"{name} returned an MCP error: {result.content}")
                print(f"\\n{name}:")
                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)

if __name__ == "__main__":
    asyncio.run(main())
