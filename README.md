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

1. Create a new folder for your ADK agent, e.g. `calculator_agent`.


2. Create a python file `agent.py` and import to `__init__.py` in the same folder:

```python
from . import agent
```

3. Implement `agent.py` with the following guide:
   - https://google.github.io/adk-docs/get-started/quickstart/

4. Create a `.env` file inside the `calculator_agent` folder with the following content:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
   ```
   **Note:** Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your actual API key.

5. Start the SSE server:

```bash
uv run sse_server.py
```

6. In another terminal, navigate to your agent folder and run:

```bash
cd agent
adk web ../
```

Your browser will open the ADK web UI, allowing you to interact with the calculator tools over the SSE transport.


# References
1. MCP SSE example:
   - https://github.com/google/adk-python/blob/main/contributing/samples/mcp_sse_agent/filesystem_server.py

2. MCP STDIO example:
   - https://github.com/google/adk-python/blob/main/contributing/samples/mcp_stdio_server_agent/agent.py
