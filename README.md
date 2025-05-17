# Calculator MCP Server

A simple MCP server exposing basic calculator operations (add, subtract, multiply, divide) as ADK FunctionTools over stdio.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

## Installation

1. Clone or download this repository.
2. In a terminal, install dependencies:

   ```bash
   uv install
   ```

## Running the Server

Start the MCP server on standard I/O:

```bash
uv run stdio_server.py
```

You should see:
```
Launching Calculator MCP Server...
```

## Using from an ADK Agent

Below is an example Python client that connects to this MCP server and invokes calculator operations:

```python
import asyncio
import json
from google.adk.tools.mcp_tool.mcp import MCPToolset
from google.adk.tools.mcp_tool.mcp import StdioServerParameters
from google.adk.agent.tool_runner import Runner

async def main():
    # Launch and connect to the server
    tools, stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="python3",
            args=["/absolute/path/to/stdio_server.py"]
        )
    )

    # Use the Runner to call a tool
    runner = Runner(tools)
    result = await runner.call_tool("add", {"a": 5, "b": 3})
    print(json.loads(result.text)["result"])  # prints 8

    # Close the connection
    await stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

Replace `/absolute/path/to/stdio_server.py` with the correct path on your system.

## Listing Available Tools

You can also list available tools using any MCP-capable client. In Python:

```python
tools, stack = await MCPToolset.from_server(
    connection_params=StdioServerParameters(
        command="python3",
        args=["/absolute/path/to/stdio_server.py"]
    )
)
print([t.name for t in tools])  # ["add", "subtract", "multiply", "divide"]
await stack.aclose()
```

## Cline MCP Configuration

If using Cline MCP, add the following configuration:

```json
{
  "mcpServers": {
    "calculator": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "<absolute_path>/calculator_mcp/",
        "run",
        "stdio_server.py"
      ]
    }
  }
}
```

## Using with adk web (SSE Server)
You can connect to the SSE-based MCP server from `adk web`. Follow these steps:

1. Create a new folder for your ADK agent, e.g. `adk_agent_sse`.
2. Inside that folder, create `agent.py` with the following:

```python
from contextlib import AsyncExitStack
import asyncio
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

async def main():
    common_exit_stack = AsyncExitStack()
    tools, _ = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8000/sse"
        ),
        async_exit_stack=common_exit_stack
    )
    agent = LlmAgent(
        model='gemini-2.0-flash',
        name='calculator_sse_agent',
        instruction='Use calculator tools via SSE.',
        tools=tools
    )

    # Example call
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService

    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    runner = Runner(
        app_name='calculator_sse_app',
        agent=agent,
        artifact_service=artifacts_service,
        session_service=session_service,
    )
    result = await runner.call_tool('add', {'a': 4, 'b': 7})
    print(result.text)
    await common_exit_stack.aclose()

if __name__ == '__main__':
    asyncio.run(main())
```

3. Create `__init__.py` in the same folder:

```python
from . import agent
```

4. Start the SSE server:

```bash
uv run sse_server.py
```

5. In another terminal, navigate to your agent folder and run:

```bash
cd adk_agent_sse
adk web
```

Your browser will open the ADK web UI, allowing you to interact with the calculator tools over the SSE transport.
