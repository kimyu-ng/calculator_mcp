"""STDIO for the calculator tool using MCP protocol."""

import asyncio
import json
import logging
from dotenv import load_dotenv

# MCP server imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK Tool imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

from calculator import add, subtract, multiply, divide

# Load environment variables (if any)
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Instantiate ADK FunctionTools
add_tool = FunctionTool(add)
subtract_tool = FunctionTool(subtract)
multiply_tool = FunctionTool(multiply)
divide_tool = FunctionTool(divide)
all_tools = [add_tool, subtract_tool, multiply_tool, divide_tool]
tool_map = {tool.name: tool for tool in all_tools}

# Create MCP server instance
app = Server("calculator-mcp-server")

@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    # Log incoming list_tools request
    logging.info("MCP Server: Received list_tools request, advertising %d tools", len(all_tools))
    """List all available calculator tools."""
    return [adk_to_mcp_tool_type(tool) for tool in all_tools]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
    # Log incoming call_tool request
    logging.info("MCP Server: Received call_tool for '%s' with args: %s", name, arguments)
    """Execute a calculator tool by name with given arguments."""
    if name in tool_map:
        try:
            result = await tool_map[name].run_async(args=arguments, tool_context=None)
            # Log successful execution
            logging.info("MCP Server: Tool '%s' executed successfully with result: %s", name, result)
            return [mcp_types.TextContent(type="text", text=json.dumps({"result": result}))]
        except Exception as e:
            # Log error during execution
            logging.error("MCP Server: Error executing tool '%s': %s", name, e)
            return [mcp_types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
    else:
        logging.warning("MCP Server: call_tool: Tool '%s' not found", name)
        return [mcp_types.TextContent(type="text", text=json.dumps({"error": f"Tool '{name}' not found."}))]

async def run_server():
    # Log server start
    logging.info("MCP Server: Starting stdio server loop")
    """Run the MCP server over standard I/O."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    # Use logging instead of print for startup/shutdown messages
    logging.info("Launching Calculator MCP Server...")
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logging.info("Calculator MCP Server stopped by user.")

    logging.info("Calculator MCP Server process exiting.")
