"""SSE server for the calculator tool using MCP protocol."""

import asyncio
import logging
from dotenv import load_dotenv
import sys

from mcp.server.fastmcp import FastMCP

# Import calculator functions with aliases to be wrapped by @mcp.tool
from calculator import add as calculator_add, \
                        subtract as calculator_subtract, \
                        multiply as calculator_multiply, \
                        divide as calculator_divide

# Load environment variables (if any)
load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

# Create FastMCP server instance
# The agent expects the server at http://localhost:8001/sse
# FastMCP defaults to /sse path when transport="sse"
mcp = FastMCP(
    "calculator-mcp-server-sse",
    host="localhost",
    port=8001
)

# Define tools using @mcp.tool decorator
@mcp.tool(description="Add two numbers.")
def add(a: float, b: float) -> float:
    """Add two numbers."""
    logging.info(f"Tool 'add' called with a={a}, b={b}")
    result = calculator_add(a, b)
    logging.info(f"Tool 'add' result: {result}")
    return result

@mcp.tool(description="Subtract b from a.")
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    logging.info(f"Tool 'subtract' called with a={a}, b={b}")
    result = calculator_subtract(a, b)
    logging.info(f"Tool 'subtract' result: {result}")
    return result

@mcp.tool(description="Multiply two numbers.")
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    logging.info(f"Tool 'multiply' called with a={a}, b={b}")
    result = calculator_multiply(a, b)
    logging.info(f"Tool 'multiply' result: {result}")
    return result

@mcp.tool(description="Divide a by b. Raises error on division by zero.")
def divide(a: float, b: float) -> float:
    """Divide a by b, error on division by zero."""
    logging.info(f"Tool 'divide' called with a={a}, b={b}")
    # Let FastMCP handle exceptions raised by calculator_divide directly
    result = calculator_divide(a, b)
    logging.info(f"Tool 'divide' result (if successful): {result}")
    return result

# Main entry point
if __name__ == "__main__":
    try:
        logging.info(f"Launching Calculator MCP SSE Server with FastMCP")
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logging.info("Calculator MCP SSE Server has been shut down.")
    except Exception as e:
        logging.error(f"Unexpected error in Calculator MCP SSE Server: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Calculator MCP SSE Server process exiting. Thank you for using the server!")
