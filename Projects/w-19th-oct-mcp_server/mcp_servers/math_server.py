from fastmcp import FastMCP
from typing import List, Union

mcp = FastMCP("Math Server")

@mcp.tool()
def add(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Add multiple numbers together. Can handle 2, 3, or more numbers.
    
    Examples:
    - "add 2, 3, 5" -> 10
    - "sum 5 and 10 and 15" -> 30
    - "add 1, 2, 3, 4, 5" -> 15
    """
    return sum(numbers)

@mcp.tool()
def multiply(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Multiply multiple numbers together. Can handle 2, 3, or more numbers.
    
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

if __name__ == "__main__":
    print("Starting Math Server...")
    mcp.run()