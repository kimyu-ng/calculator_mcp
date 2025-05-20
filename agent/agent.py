import asyncio
import json
from typing import Any

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    SseServerParams,
)

load_dotenv()

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="assistant",
    instruction="""Help user to perform calculations using the calculator tools.
    Once you compute the result, always show step by step calculation.
    """,
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url="http://localhost:8001/sse",
            )
        )
    ],
)
