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

## License

[MIT](LICENSE)
