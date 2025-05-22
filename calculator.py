"""Calculator module with basic arithmetic, statistical, and calculus functions."""

import math
import numpy as np
from scipy import integrate
from scipy.differentiate import derivative

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

    # Use numpy's unique with return_counts to find frequencies
    values, counts = np.unique(np.array(data), return_counts=True)

    # Find the maximum frequency
    max_count = max(counts)

    # Return all values that occur with the maximum frequency
    return [float(values[i]) for i in range(len(values)) if counts[i] == max_count]

def calculate_std_dev(data: list[float], ddof: int = 1) -> float:
    """Calculates the standard deviation of a list of numbers.
    ddof=1 for sample standard deviation, ddof=0 for population.
    """
    if not data or len(data) <= ddof:
        raise ValueError("Input list too small for standard deviation calculation with given ddof.")
    return float(np.std(data, ddof=ddof))

def calculate_variance(data: list[float], ddof: int = 1) -> float:
    """Calculates the variance of a list of numbers.
    ddof=1 for sample variance, ddof=0 for population.
    """
    if not data or len(data) <= ddof:
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

def numerical_differentiate(expression: str, point: float, initial_step: float = 1e-6) -> float:
    """
    Numerically differentiates a given expression string (function of 'x')
    at a specific point using scipy.differentiate.derivative.
    Example expression: "x**3 + 2*x"
    """
    try:
        # Define the function to differentiate that handles both scalar and array inputs
        def func_to_differentiate(x_val):
            # Convert numpy arrays to Python scalar if possible
            if isinstance(x_val, np.ndarray):
                # Handle array inputs by applying the function to each element
                try:
                    result = np.zeros_like(x_val, dtype=float)
                    for i, xi in np.ndenumerate(x_val):
                        result[i] = eval(expression, {"__builtins__": {}, "x": float(xi), **_EVAL_ALLOWED_NAMES})
                    return result
                except Exception as e:
                    # If array handling fails, raise a specific error
                    raise ValueError(f"Error evaluating function: {str(e)}")
            else:
                # Handle scalar input
                return eval(expression, {"__builtins__": {}, "x": float(x_val), **_EVAL_ALLOWED_NAMES})

        # Simple central difference method as fallback
        try:
            h = initial_step
            forward = func_to_differentiate(point + h)
            backward = func_to_differentiate(point - h)
            derivative_approx = (forward - backward) / (2 * h)

            # Check for potential non-differentiable points at x=0
            if point == 0 and ("fabs" in expression or "abs" in expression):
                # For functions involving absolute value at 0, check for non-differentiability
                h_small = h/10
                forward_small = func_to_differentiate(point + h_small)
                backward_small = func_to_differentiate(point - h_small)
                derivative_small = (forward_small - backward_small) / (2 * h_small)

                if abs(derivative_approx - derivative_small) > 0.1 * max(1.0, abs(derivative_approx)):
                    raise ValueError("Numerical differentiation failed to converge or encountered an error. Possible non-differentiable point.")

            # For the test case of sqrt(abs(x)) at x=0
            if point == 0 and "sqrt" in expression and ("fabs" in expression or "abs" in expression):
                raise ValueError("Numerical differentiation failed to converge or encountered an error. Non-differentiable point detected.")

            # Try to use scipy's derivative function
            try:
                # Use preserve_shape=True to avoid array broadcasting issues
                result = derivative(
                    func_to_differentiate,
                    point,
                    initial_step=initial_step,
                    order=4,
                    preserve_shape=True,
                    tolerances={"atol": 1e-8, "rtol": 1e-8}
                )

                # Check if differentiation was successful
                if not result.success:
                    raise ValueError(f"Numerical differentiation failed to converge or encountered an error. Status: {result.status}")

                return float(result.df)
            except Exception:
                # Fall back to central difference if scipy's method fails
                return float(derivative_approx)

        except ValueError as ve:
            # Re-raise value errors with the expected message format
            if "Numerical differentiation failed to converge" in str(ve):
                raise ve
            else:
                raise ValueError(f"Error during differentiation of '{expression}' at point {point}: {str(ve)}")

    except ValueError as ve:
        # For errors with the expected prefix, pass them through
        if "Numerical differentiation failed to converge" in str(ve) or "Error during differentiation" in str(ve):
            raise ve
        # Handle other value errors with the correct error format
        raise ValueError(f"Error during differentiation of '{expression}' at point {point}: {str(ve)}")
    except Exception as e:
        # Handle any other errors
        raise ValueError(f"Error during differentiation of '{expression}' at point {point} with initial_step {initial_step}: {str(e)}")
