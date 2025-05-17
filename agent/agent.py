import asyncio
import json
from typing import Any

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,  # Optional
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import (
  MCPToolset,
  SseServerParams,
)
from google.genai import types
from rich import print
load_dotenv()


async def get_tools_async():
    """Gets tools from the File System MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8001/sse",
        )
    )
    print("MCP Toolset created successfully.")
    return tools, exit_stack


async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server."""
    tools, exit_stack = await get_tools_async()
    print(f"Fetched {len(tools)} tools from MCP server.")
    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
        instruction="""Help user to perform calculations using the calculator tools.
        Once you compute the result, always show step by step calculation.
        """,
        tools=tools,
    )
    return root_agent, exit_stack

if __name__ == "__main__":
  root_agent = get_agent_async()
