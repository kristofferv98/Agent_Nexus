# functions/math_tools.py

def subtract_numbers(a: float, b: float) -> float:
    """Subtracts b from a and returns the result."""
    print(f"Subtracting {a} and {b} = {a - b}")
    return a - b

def add_numbers(a: float, b: float) -> float:
    """Adds two numbers and returns the result."""
    print(f"Adding {a} and {b} = {a + b}")
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Multiplies two numbers and returns the result."""
    print(f"Multiplying {a} and {b} = {a * b}")
    return a * b

def divide_numbers(a: float, b: float) -> float:
    """Divides a by b and returns the result."""
    print(f"Dividing {a} and {b} = {a / b}")
    return a / b

def square_number(a: float) -> float:
    """Squares a number and returns the result."""
    print(f"Squaring {a} = {a ** 2}")
    return a ** 2

def cube_number(a: float) -> float:
    """Cubes a number and returns the result."""
    print(f"Cubing {a} = {a ** 3}")
    return a ** 3