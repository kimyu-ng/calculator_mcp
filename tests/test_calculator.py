import pytest
import math

from calculator import (
    add,
    subtract,
    multiply,
    divide,
    evaluate_expression,
    calculate_mean,
    calculate_median,
    calculate_mode,
    calculate_std_dev,
    calculate_variance,
    numerical_integrate,
    numerical_differentiate,
)

# Test basic arithmetic operations
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(-1, -1) == -2
    assert add(1.5, 2.5) == 4.0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(0, 0) == 0
    assert subtract(2.5, 1.5) == 1.0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 5) == -5
    assert multiply(0, 100) == 0
    assert multiply(1.5, 2.0) == 3.0

def test_divide():
    assert divide(6, 3) == 2
    assert divide(5, 2) == 2.5
    assert divide(0, 5) == 0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        divide(1, 0)

# Test expression evaluation
def test_evaluate_expression_simple():
    assert evaluate_expression("2 + 3 * 4") == 14  # 2 + 12
    assert evaluate_expression("(2 + 3) * 4") == 20 # 5 * 4
    assert evaluate_expression("10 / 2 - 1") == 4   # 5 - 1
    assert evaluate_expression("2**3") == 8

def test_evaluate_expression_with_math_functions():
    assert evaluate_expression("math.sqrt(16)") == pytest.approx(4.0)
    assert evaluate_expression("math.sin(math.pi/2)") == pytest.approx(1.0)
    assert evaluate_expression("math.log(math.e)") == pytest.approx(1.0)
    assert evaluate_expression("pow(2, 3)") == pytest.approx(8.0)
    assert evaluate_expression("sqrt(9)") == pytest.approx(3.0) # Direct access

def test_evaluate_expression_invalid():
    with pytest.raises(ValueError, match="Invalid mathematical expression or disallowed function/variable"):
        evaluate_expression("2 +")
    with pytest.raises(ValueError, match="Invalid mathematical expression or disallowed function/variable"):
        evaluate_expression("import os") # Disallowed
    with pytest.raises(ValueError, match="Invalid mathematical expression or disallowed function/variable"):
        evaluate_expression("unknown_func(5)")
    with pytest.raises(ValueError, match="Expression did not evaluate to a numeric value."):
        evaluate_expression("math.sin") # Not a number

def test_evaluate_expression_division_by_zero():
    with pytest.raises(ValueError, match="Division by zero is not allowed in the expression."):
        evaluate_expression("1 / 0")
    with pytest.raises(ValueError, match="Division by zero is not allowed in the expression."):
        evaluate_expression("1 / (2-2)")


# Test statistical functions
def test_calculate_mean():
    assert calculate_mean([1, 2, 3, 4, 5]) == 3.0
    assert calculate_mean([10, 20, 30]) == 20.0
    assert calculate_mean([-1, 0, 1]) == 0.0
    assert calculate_mean([2.5, 3.5]) == 3.0

def test_calculate_mean_empty():
    with pytest.raises(ValueError, match="Input list cannot be empty for mean calculation."):
        calculate_mean([])

def test_calculate_median():
    assert calculate_median([1, 2, 3, 4, 5]) == 3.0
    assert calculate_median([1, 2, 3, 4]) == 2.5 # (2+3)/2
    assert calculate_median([10, 5, 2]) == 5.0 # Sorted: 2, 5, 10
    assert calculate_median([7]) == 7.0

def test_calculate_median_empty():
    with pytest.raises(ValueError, match="Input list cannot be empty for median calculation."):
        calculate_median([])

def test_calculate_mode():
    assert sorted(calculate_mode([1, 2, 2, 3, 4])) == sorted([2.0])
    assert sorted(calculate_mode([1, 1, 2, 2, 3])) == sorted([1.0, 2.0]) # Multimodal
    assert sorted(calculate_mode([1, 2, 3, 4, 5])) == sorted([1.0, 2.0, 3.0, 4.0, 5.0]) # All unique
    assert sorted(calculate_mode([5, 5, 5])) == sorted([5.0])

def test_calculate_mode_empty():
    with pytest.raises(ValueError, match="Input list cannot be empty for mode calculation."):
        calculate_mode([])

def test_calculate_std_dev():
    assert calculate_std_dev([1, 2, 3, 4, 5], ddof=1) == pytest.approx(math.sqrt(2.5))
    assert calculate_std_dev([1, 2, 3, 4, 5], ddof=0) == pytest.approx(math.sqrt(2.0))

def test_calculate_std_dev_errors():
    with pytest.raises(ValueError, match="Input list too small for standard deviation calculation with given ddof."):
        calculate_std_dev([], ddof=1)
    with pytest.raises(ValueError, match="Input list too small for standard deviation calculation with given ddof."):
        calculate_std_dev([1], ddof=1) # Needs at least 2 for ddof=1
    assert calculate_std_dev([1], ddof=0) == 0.0 # Population std dev of single point is 0

def test_calculate_variance():
    assert calculate_variance([1, 2, 3, 4, 5], ddof=1) == pytest.approx(2.5)
    assert calculate_variance([1, 2, 3, 4, 5], ddof=0) == pytest.approx(2.0)

def test_calculate_variance_errors():
    with pytest.raises(ValueError, match="Input list too small for variance calculation with given ddof."):
        calculate_variance([], ddof=1)
    with pytest.raises(ValueError, match="Input list too small for variance calculation with given ddof."):
        calculate_variance([1], ddof=1)
    assert calculate_variance([1], ddof=0) == 0.0

# Test calculus functions
def test_numerical_integrate():
    # Integral of x from 0 to 1 is 0.5
    assert numerical_integrate("x", 0, 1) == pytest.approx(0.5)
    # Integral of x^2 from 0 to 1 is 1/3
    assert numerical_integrate("x**2", 0, 1) == pytest.approx(1/3)
    # Integral of sin(x) from 0 to pi is 2
    assert numerical_integrate("math.sin(x)", 0, math.pi) == pytest.approx(2.0)

def test_numerical_integrate_invalid_expression():
    with pytest.raises(ValueError, match="Error during integration"):
        numerical_integrate("1/x", -1, 1) # Singularity
    with pytest.raises(ValueError, match="Error during integration"):
        numerical_integrate("nonexistent_func(x)", 0, 1)

def test_numerical_differentiate():
    # Derivative of x^2 at x=2 is 2*x = 4
    assert numerical_differentiate("x**2", 2) == pytest.approx(4.0)
    # Derivative of x^3 at x=1 is 3*x^2 = 3
    assert numerical_differentiate("x**3", 1) == pytest.approx(3.0)
    # Derivative of sin(x) at x=0 is cos(0) = 1
    assert numerical_differentiate("math.sin(x)", 0) == pytest.approx(1.0)
    # Derivative of exp(x) at x=0 is exp(0) = 1
    assert numerical_differentiate("math.exp(x)", 0) == pytest.approx(1.0)

def test_numerical_differentiate_invalid_expression():
    with pytest.raises(ValueError, match="Error during differentiation"):
        numerical_differentiate("nonexistent_func(x)", 1)
    # Test for a case that might lead to convergence issues if not handled by scipy
    # For example, a function with a sharp turn or discontinuity, though scipy's method is robust.
    # This specific test might depend on scipy's internal error handling.
    # Example: derivative of abs(x) at x=0 is undefined.
    # Scipy's derivative might return a result but with a large error or failure status.
    # The current implementation checks res.success.
    with pytest.raises(ValueError, match="Numerical differentiation failed to converge or encountered an error"):
        # A function that might be problematic for numerical differentiation at 0
        # For example, a function that is not smooth enough or has issues.
        # Let's try a function that might cause issues, e.g., sqrt(abs(x)) at 0
        # This is just an example, actual behavior depends on scipy's robustness
        numerical_differentiate("math.sqrt(math.fabs(x))", 0, initial_step=1e-8)

def test_numerical_differentiate_with_step():
    assert numerical_differentiate("x**2", 2, initial_step=1e-5) == pytest.approx(4.0)
