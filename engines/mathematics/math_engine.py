# Updated Math Engine

This math engine now includes robust expression parsing, calculus support for derivatives and integrals, and improved variable extraction. It also provides step-by-step solutions for mathematical problems.

## Features
1. **Robust Expression Parsing**: Handles a variety of mathematical expressions and ensures accurate interpretation.
2. **Calculus Support**:
   - Derivatives: Compute the derivative of functions.
   - Integrals: Calculate definite and indefinite integrals.
3. **Step-by-Step Solutions**: Offers detailed breakdowns of the solutions, making it easier to understand the processes.
4. **Enhanced Variable Extraction**: Automatically identifies and extracts variables from mathematical expressions.

## Usage
Here's how to utilize the updated features in your calculations:

```python
# Example of using the updated math engine
from math_engine import MathEngine

math_engine = MathEngine()
result = math_engine.calculate("integrate x^2")  # Example for integration
print(result)
```

## Todo
- Add unit tests for new features.
- Optimize performance for large expressions.
