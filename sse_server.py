"""SSE server for the calculator tool using MCP protocol."""

import sys
import logging
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# Import calculator functions with aliases to be wrapped by @mcp.tool
from calculator import (
    add as calculator_add,
    subtract as calculator_subtract,
    multiply as calculator_multiply,
    divide as calculator_divide,
    evaluate_expression as calculator_evaluate_expression,
    calculate_mean as calculator_mean,
    calculate_median as calculator_median,
    calculate_mode as calculator_mode,
    calculate_std_dev as calculator_std_dev,
    calculate_variance as calculator_variance,
    numerical_integrate as calculator_integrate,
    numerical_differentiate as calculator_differentiate
)

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
    logging.info("Tool 'add' called with a=%s, b=%s", a, b)
    result = calculator_add(a, b)
    logging.info("Tool 'add' result: %s", result)
    return result

@mcp.tool(description="Subtract b from a.")
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    logging.info("Tool 'subtract' called with a=%s, b=%s", a, b)
    result = calculator_subtract(a, b)
    logging.info("Tool 'subtract' result: %s", result)
    return result

@mcp.tool(description="Multiply two numbers.")
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    logging.info("Tool 'multiply' called with a=%s, b=%s", a, b)
    result = calculator_multiply(a, b)
    logging.info("Tool 'multiply' result: %s", result)
    return result

@mcp.tool(description="Divide a by b. Raises error on division by zero.")
def divide(a: float, b: float) -> float:
    """Divide a by b, error on division by zero."""
    logging.info("Tool 'divide' called with a=%s, b=%s", a, b)
    # Let FastMCP handle exceptions raised by calculator_divide directly
    result = calculator_divide(a, b)
    logging.info("Tool 'divide' result (if successful): %s", result)
    return result

@mcp.tool(description="Evaluates a mathematical expression string (e.g., '(2+3)*4'). Supports PEMDAS/BODMAS. WARNING: Uses eval(), ensure input is trusted.")
def evaluate(expression: str) -> float:
    """
    Evaluates a mathematical expression string like "(5 + 3) * 2 / 4 - 1".
    This tool uses Python's eval() for evaluation, which correctly handles
    standard order of operations (PEMDAS/BODMAS).

    IMPORTANT SECURITY NOTE: The underlying eval() function can execute
    arbitrary Python code if the input 'expression' is not strictly a
    mathematical formula. Ensure that expressions sent to this tool are
    from trusted sources or are thoroughly sanitized.
    """
    logging.info("Tool 'evaluate' called with expression='%s'", expression)
    try:
        result = calculator_evaluate_expression(expression)
        logging.info("Tool 'evaluate' result: %s", result)
        return result
    except (ValueError, ZeroDivisionError) as e: # Catch errors from calculator_evaluate_expression
        logging.error("Tool 'evaluate' error for expression '%s': %s", expression, e)
        raise # Re-raise for FastMCP to handle and send to client
    except Exception as e:
        logging.error("Tool 'evaluate' unexpected error for expression '%s': %s", expression, e, exc_info=True)
        raise # Re-raise for FastMCP to handle

# New statistical and calculus tools

@mcp.tool(description="Calculates the mean (average) of a list of numbers.")
def mean(data: list[float]) -> float:
    """Calculates the mean of a list of numbers."""
    logging.info("Tool 'mean' called with data: %s", data)
    try:
        result = calculator_mean(data)
        logging.info("Tool 'mean' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'mean' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'mean' unexpected error: %s", e, exc_info=True)
        raise

@mcp.tool(description="Calculates the median of a list of numbers.")
def median(data: list[float]) -> float:
    """Calculates the median of a list of numbers."""
    logging.info("Tool 'median' called with data: %s", data)
    try:
        result = calculator_median(data)
        logging.info("Tool 'median' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'median' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'median' unexpected error: %s", e, exc_info=True)
        raise

@mcp.tool(description="Calculates the mode(s) of a list of numbers. Returns a list of modes.")
def mode(data: list[float]) -> list[float]:
    """Calculates the mode(s) of a list of numbers."""
    logging.info("Tool 'mode' called with data: %s", data)
    try:
        result = calculator_mode(data)
        logging.info("Tool 'mode' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'mode' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'mode' unexpected error: %s", e, exc_info=True)
        raise

@mcp.tool(description="Calculates the sample standard deviation of a list of numbers (ddof=1).")
def std_dev(data: list[float], ddof: int = 1) -> float:
    """Calculates the standard deviation (sample by default)."""
    logging.info("Tool 'std_dev' called with data: %s, ddof: %s", data, ddof)
    try:
        result = calculator_std_dev(data, ddof)
        logging.info("Tool 'std_dev' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'std_dev' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'std_dev' unexpected error: %s", e, exc_info=True)
        raise

@mcp.tool(description="Calculates the sample variance of a list of numbers (ddof=1).")
def variance(data: list[float], ddof: int = 1) -> float:
    """Calculates the variance (sample by default)."""
    logging.info("Tool 'variance' called with data: %s, ddof: %s", data, ddof)
    try:
        result = calculator_variance(data, ddof)
        logging.info("Tool 'variance' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'variance' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'variance' unexpected error: %s", e, exc_info=True)
        raise

@mcp.tool(description="Numerically integrates an expression string (func of 'x') over an interval [a, b]. E.g., expression='x**2', a=0, b=1.")
def integrate(expression: str, lower_bound: float, upper_bound: float) -> float:
    """Numerically integrates an expression string."""
    logging.info("Tool 'integrate' called with expression='%s', lower_bound=%s, upper_bound=%s", expression, lower_bound, upper_bound)
    try:
        result = calculator_integrate(expression, lower_bound, upper_bound)
        logging.info("Tool 'integrate' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'integrate' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'integrate' unexpected error: %s", e, exc_info=True)
        raise

@mcp.tool(description="Numerically differentiates an expression string (func of 'x') at a point. E.g., expression='x**2', point=2.")
def differentiate(expression: str, point: float) -> float:
    """Numerically differentiates an expression string at a point."""
    logging.info("Tool 'differentiate' called with expression='%s', point=%s", expression, point)
    try:
        result = calculator_differentiate(expression, point)
        logging.info("Tool 'differentiate' result: %s", result)
        return result
    except ValueError as e:
        logging.error("Tool 'differentiate' error: %s", e)
        raise
    except Exception as e:
        logging.error("Tool 'differentiate' unexpected error: %s", e, exc_info=True)
        raise

# Main entry point
if __name__ == "__main__":
    try:
        logging.info("Launching Calculator MCP SSE Server with FastMCP")
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logging.info("Calculator MCP SSE Server has been shut down.")
    except Exception as e:
        logging.error("Unexpected error in Calculator MCP SSE Server: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Calculator MCP SSE Server process exiting. Thank you for using the server!")
