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
3. Create virtual environment
   ```bash
   uv venv
   source .venv/bin/activate
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

## Using `calculator_agent` with Gemini (via adk web SSE Server)

This section explains how to connect the `calculator_agent` (configured for Gemini) to the SSE-based MCP server using `adk web`.

1. Create a new folder for your ADK agent, e.g., `calculator_agent`. (This folder should already exist if you cloned the repository).

2. Ensure `calculator_agent/agent.py` is configured for Gemini (e.g., `model="gemini-2.0-flash"`).

3. Create or verify the `.env` file inside the `calculator_agent` folder with the following content for Gemini:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
   ```
   **Note:** Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your actual Google API key.

4. Start the SSE server from the `calculator_mcp` root directory:
   ```bash
   uv run sse_server.py
   ```

5. In another terminal, navigate to your `calculator_agent` folder and run `adk web` pointing to its parent directory:
   ```bash
   cd path/to/your/calculator_agent
   adk web ../
   ```
   For example, if `calculator_agent` is inside `calculator_mcp`, and you are in `calculator_mcp/calculator_agent`, you would run `adk web ../`. If `calculator_agent` is a sibling to `calculator_mcp`, you might run `adk web ../calculator_agent` from within `calculator_mcp` or adjust paths accordingly. The key is that `adk web` needs to find the agent's directory.

Your browser will open the ADK web UI, allowing you to interact with the calculator tools using the Gemini-powered `calculator_agent`.

## Using `calculator_agent_litellm` with Other LLMs (e.g., OpenAI)

This section describes how to run the `calculator_agent_litellm` example agent using non-Gemini models like OpenAI, leveraging LiteLLM.

### Configuring `calculator_agent_litellm` for OpenAI

The `calculator_agent_litellm` uses LiteLLM, which simplifies using various LLM providers, including OpenAI.

1.  **Set Environment Variables for OpenAI:**
    Create or update a `.env` file in the root of your `calculator_agent_litellm` project folder.
    For OpenAI, you primarily need to set:

    ```env
    # Required: Your OpenAI API key
    OPENAI_API_KEY="your_openai_api_key_here"

    # Optional: LiteLLM allows specifying the model directly in the agent code
    # (as done in the example agent.py: model="openai/gpt-4.1-nano")
    # or via other environment variables if your agent code is set up to read them.
    # If agent.py uses a generic "MODEL" env var for LiteLLM model string:
    # MODEL="openai/gpt-4"
    ```
    Replace `your_openai_api_key_here` with your actual OpenAI API key. LiteLLM will automatically use this for OpenAI calls if the model string in `agent.py` (e.g., `openai/gpt-4.1-nano`) indicates an OpenAI model.

2.  **Ensure Agent Code Specifies an OpenAI Model:**
    Verify that your `agent.py` within `calculator_agent_litellm` is configured to use an OpenAI model string recognized by LiteLLM (e.g., `"openai/o4-mini"`, `"gpt-4.1-nano"` if it's an OpenAI model). The example uses `model="openai/gpt-4.1-nano"`.
    ```python
    # In calculator_agent_litellm/agent.py
    # root_agent = LlmAgent(
    #     model=LiteLlm(
    #         model="openai/gpt-4.1-nano", # This specifies an OpenAI model via LiteLLM
    #         api_key=os.getenv("MY_OPENAI_API_KEY"), # Ensure this matches your .env key if different
    #     ),
    # ...
    # )
    ```
    Note: The example `agent.py` for `calculator_agent_litellm` uses `os.getenv("MY_OPENAI_API_KEY")`. Ensure your `.env` file for `calculator_agent_litellm` uses `MY_OPENAI_API_KEY` or update the `agent.py` to use `OPENAI_API_KEY`. For consistency with common practices, using `OPENAI_API_KEY` in both the `.env` file and `os.getenv()` is recommended.

3.  **Start the SSE Server (if not already running):**
    In your `calculator_mcp` project root:
    ```bash
    uv run sse_server.py
    ```

4.  **Run the ADK Web UI for `calculator_agent_litellm`:**
    In another terminal, navigate to your `calculator_agent_litellm` folder and run `adk web` pointing to its parent directory or the agent directory itself as appropriate:
    ```bash
    cd path/to/your/calculator_agent_litellm
    adk web ../
    ```
    The agent will use LiteLLM to proxy requests to the specified OpenAI model using your API key.

# References
1. MCP SSE example:
   - https://github.com/google/adk-python/blob/main/contributing/samples/mcp_sse_agent/filesystem_server.py

2. MCP STDIO example:
   - https://github.com/google/adk-python/blob/main/contributing/samples/mcp_stdio_server_agent/agent.py

3. Setting up runtime keys
   - https://docs.litellm.ai/docs/set_keys
