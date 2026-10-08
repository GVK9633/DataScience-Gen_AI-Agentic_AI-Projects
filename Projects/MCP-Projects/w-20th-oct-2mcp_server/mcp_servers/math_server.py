from fastmcp import FastMCP
from typing import List, Union
import json

mcp = FastMCP("Math Server")

@mcp.tool()
def add(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Add multiple numbers together. Can handle 2, 3, or more numbers.
    
    Args:
        numbers: List of numbers to add together
        
    Examples:
        - "add 2, 3, 5" -> 10
        - "sum 5 and 10 and 15" -> 30
        - "add 1, 2, 3, 4, 5" -> 15
    """
    return sum(numbers)

@mcp.tool()
def multiply(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Multiply multiple numbers together. Can handle 2, 3, or more numbers.
    
    Args:
        numbers: List of numbers to multiply together
        
    Examples:
        - "multiply 2, 3, 4" -> 24
        - "product of 5 and 10" -> 50
        - "multiply 1, 2, 3, 4" -> 24
    """
    result = 1
    for num in numbers:
        result *= num
    return result

@mcp.tool()
def subtract(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Subtract numbers in sequence. First number minus the rest.
    
    Args:
        numbers: List where first number is minuend, rest are subtrahends
        
    Examples:
        - "subtract 10, 5" -> 5
        - "10 minus 3 minus 2" -> 5
    """
    if not numbers:
        return 0
    result = numbers[0]
    for num in numbers[1:]:
        result -= num
    return result

@mcp.tool()
def divide(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Divide numbers in sequence. First number divided by the rest.
    
    Args:
        numbers: List where first number is dividend, rest are divisors
        
    Examples:
        - "divide 10, 2" -> 5
        - "20 divided by 2 divided by 5" -> 2
    """
    if not numbers:
        return 0
    result = numbers[0]
    for num in numbers[1:]:
        if num == 0:
            raise ValueError("Cannot divide by zero")
        result /= num
    return result

# Add a simple text-based tool for compatibility
# @mcp.tool()
# def calculate(operation: str, numbers: List[Union[int, float]]) -> Union[int, float]:
#     """Perform basic calculations with text operation.
    
#     Args:
#         operation: One of 'add', 'multiply', 'subtract', 'divide'
#         numbers: List of numbers to operate on
#     """
#     if operation == 'add':
#         return sum(numbers)
#     elif operation == 'multiply':
#         result = 1
#         for num in numbers:
#             result *= num
#         return result
#     elif operation == 'subtract':
#         if not numbers:
#             return 0
#         result = numbers[0]
#         for num in numbers[1:]:
#             result -= num
#         return result
#     elif operation == 'divide':
#         if not numbers:
#             return 0
#         result = numbers[0]
#         for num in numbers[1:]:
#             if num == 0:
#                 raise ValueError("Cannot divide by zero")
#             result /= num
#         return result
#     else:
#         raise ValueError(f"Unknown operation: {operation}")

if __name__ == "__main__":
    print("Starting Math Server...")
    mcp.run(transport="stdio")