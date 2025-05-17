"""SSE server for the calculator tool using MCP protocol."""

import asyncio
import json
import logging
from dotenv import load_dotenv

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

# MCP server imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport

# ADK Tool imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

from calculator import add, subtract, multiply, divide

# Load environment variables (if any)
load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

# Define calculator functions
# ...existing code...
# Instantiate ADK FunctionTools
add_tool = FunctionTool(add)
subtract_tool = FunctionTool(subtract)
multiply_tool = FunctionTool(multiply)
divide_tool = FunctionTool(divide)
all_tools = [add_tool, subtract_tool, multiply_tool, divide_tool]
tool_map = {tool.name: tool for tool in all_tools}

# Create MCP server instance
mcp_server = Server("calculator-mcp-server-sse")


@mcp_server.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    logging.info(
      "MCP SSE Server: Received list_tools request, advertising %d tools", len(all_tools))
    return [adk_to_mcp_tool_type(tool) for tool in all_tools]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
    logging.info(
        "MCP SSE Server: Received call_tool for '%s' with args: %s", name, arguments)
    if name in tool_map:
        try:
            result = await tool_map[name].run_async(args=arguments, tool_context=None)
            logging.info(
                "MCP SSE Server: Tool '%s' executed successfully with result: %s", name, result)
            return [mcp_types.TextContent(type="text", text=json.dumps({"result": result}))]
        except Exception as e:
            logging.error(
                "MCP SSE Server: Error executing tool '%s': %s", name, e)
            return [mcp_types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
    else:
        logging.warning("MCP SSE Server: call_tool: Tool '%s' not found", name)
        return [
          mcp_types.TextContent(
            type="text",
            text=json.dumps({"error": f"Tool '{name}' not found."})
          )
        ]

sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> None:
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await mcp_server.run(reader, writer, InitializationOptions(
            server_name=mcp_server.name,
            server_version="0.1.0",
            capabilities=mcp_server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        ))

app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    try:
        logging.info("Launching Calculator MCP SSE Server...")
        uvicorn.run(app, host="localhost", port=8001)
    except KeyboardInterrupt:
        logging.info("Calculator MCP SSE Server stopped by user.")
    logging.info("Calculator MCP SSE Server process exiting.")
