import math
import numpy as np
from scipy import integrate
from scipy.differentiate import derivative
from scipy import stats

# Define calculator functions

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide a by b, error on division by zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


# Define a dictionary of allowed names for the eval() context
# This includes common math functions and constants.
_EVAL_ALLOWED_NAMES = {
    "math": math,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "pow": math.pow,
    "fabs": math.fabs,
    "pi": math.pi,
    "e": math.e,
    # Numpy functions can also be added if desired for use within expressions
    # "np": np, # Be cautious about exposing too much of numpy
}

def evaluate_expression(expression: str) -> float:
    """
    Evaluates a mathematical expression string respecting PEMDAS/BODMAS using a safer eval.

    WARNING: While safer than a wide-open eval(), this approach still carries risks
    if the expression string can be crafted maliciously. For highly sensitive
    applications, a dedicated parsing library is recommended.

    Allowed operations include +, -, *, /, parentheses, and functions/constants
    from the math module (e.g., sin, cos, pi, e, sqrt, log).
    """
    try:
        # Python's eval() handles order of operations (PEMDAS/BODMAS)
        # and parentheses naturally.
        result = eval(expression, {"__builtins__": {}}, _EVAL_ALLOWED_NAMES)

        if not isinstance(result, (int, float)):
            raise ValueError("Expression did not evaluate to a numeric value.")
        return float(result)
    except (SyntaxError, NameError, TypeError) as e:
        # Catch common errors during parsing or evaluation of the expression
        # NameError will occur if the expression uses functions/variables not in allowed_names
        raise ValueError(f"Invalid mathematical expression or disallowed function/variable: {str(e)}")
    except ZeroDivisionError:
        raise ValueError("Division by zero is not allowed in the expression.")
    # Other unexpected errors during eval will also propagate.

# Statistical functions
def calculate_mean(data: list[float]) -> float:
    """Calculates the mean (average) of a list of numbers."""
    if not data:
        raise ValueError("Input list cannot be empty for mean calculation.")
    return float(np.mean(data))

def calculate_median(data: list[float]) -> float:
    """Calculates the median of a list of numbers."""
    if not data:
        raise ValueError("Input list cannot be empty for median calculation.")
    return float(np.median(data))

def calculate_mode(data: list[float]) -> list[float]:
    """Calculates the mode(s) of a list of numbers. Can return multiple modes."""
    if not data:
        raise ValueError("Input list cannot be empty for mode calculation.")
    # scipy.stats.mode can handle multimodal distributions.
    # It returns a ModeResult object with attributes 'mode' and 'count'.
    # 'mode' can be an array if there are multiple modes.
    mode_result = stats.mode(np.array(data), keepdims=False) # keepdims=False for compatibility
    # Ensure mode_result.mode is iterable and convert to list of floats
    modes = mode_result.mode
    if isinstance(modes, np.ndarray):
        return [float(m) for m in modes]
    return [float(modes)] # Single mode

def calculate_std_dev(data: list[float], ddof: int = 1) -> float:
    """Calculates the standard deviation of a list of numbers.
    ddof=1 for sample standard deviation, ddof=0 for population.
    """
    if not data or len(data) < ddof:
        raise ValueError("Input list too small for standard deviation calculation with given ddof.")
    return float(np.std(data, ddof=ddof))

def calculate_variance(data: list[float], ddof: int = 1) -> float:
    """Calculates the variance of a list of numbers.
    ddof=1 for sample variance, ddof=0 for population.
    """
    if not data or len(data) < ddof:
        raise ValueError("Input list too small for variance calculation with given ddof.")
    return float(np.var(data, ddof=ddof))

# Calculus functions
def numerical_integrate(expression: str, lower_bound: float, upper_bound: float) -> float:
    """
    Numerically integrates a given expression string (function of 'x')
    from a lower_bound to an upper_bound.
    Example expression: "x**2 * math.sin(x)"
    """
    try:
        # Define the function to integrate using a lambda and restricted eval
        # The variable 'x' will be available in the expression's scope.
        func_to_integrate = lambda x: eval(expression, {"__builtins__": {}, "x": x, **_EVAL_ALLOWED_NAMES})

        # Perform the integration
        result, _error = integrate.quad(func_to_integrate, lower_bound, upper_bound)
        # You might want to log or handle the 'error' (estimated error of integration)
        return float(result)
    except Exception as e:
        raise ValueError(f"Error during integration of '{expression}': {str(e)}")

def numerical_differentiate(expression: str, point: float, initial_step: float = 1e-6) -> float: # Renamed dx to initial_step
    """
    Numerically differentiates a given expression string (function of 'x')
    at a specific point using scipy.differentiate.derivative.
    Example expression: "x**3 + 2*x"
    """
    try:
        # Define the function to differentiate
        # Using x_val to avoid potential clashes if 'x' is in _EVAL_ALLOWED_NAMES
        func_to_differentiate = lambda x_val: eval(expression, {"__builtins__": {}, "x": x_val, **_EVAL_ALLOWED_NAMES})

        # Perform the differentiation using scipy.differentiate.derivative
        # It returns a result object; the derivative is in the 'df' attribute.
        res = derivative(func_to_differentiate, point, initial_step=initial_step)

        if not res.success:
            # res.status provides more detail on failure:
            # 0: Success
            # -1: Error estimate increased
            # -2: Max iterations reached
            # -3: Non-finite value encountered
            # -4: Iteration terminated by callback
            raise ValueError(f"Numerical differentiation failed to converge or encountered an error. Status: {res.status}. Error estimate: {res.error}")

        return float(res.df) # The derivative is in the 'df' attribute
    except ValueError as ve: # Catch specific ValueErrors from above or eval
        raise ve
    except Exception as e:
        # Catch other potential errors from eval or the derivative call
        raise ValueError(f"Error during differentiation of '{expression}' at point {point} with initial_step {initial_step}: {str(e)}")
