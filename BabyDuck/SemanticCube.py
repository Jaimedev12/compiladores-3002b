from typing import Union


class SemanticCube:
    def __init__(self):
        self.cube = {
            "int": {
                "int": {
                    "+": "int",
                    "-": "int",
                    "*": "int",
                    "/": "int",
                    "<": "int",
                    ">": "int",
                    "!=": "int",
                },
                "float": {
                    "+": "float",
                    "-": "float",
                    "*": "float",
                    "/": "float",
                    "<": "int",
                    ">": "int",
                    "!=": "int",
                }
            },
            "float": {
                "int": {
                    "+": "float",
                    "-": "float",
                    "*": "float",
                    "/": "float",
                    "<": "int",
                    ">": "int",
                    "!=": "int",
                },
                "float": {
                    "+": "float",
                    "-": "float",
                    "*": "float",
                    "/": "float",
                    "<": "int",
                    ">": "int",
                    "!=": "int",
                }
            }
        }

        self.valid_declarations = {
            "int": {
                "int": lambda x: x,  # No conversion needed
                "float": lambda x: int(x)  # Convert float to int (truncation)
            },
            "float": {
                "int": lambda x: float(x),  # Convert int to float
                "float": lambda x: x  # No conversion needed
            }
        }

    def get_resulting_type(self, type1, type2, operation) -> str:
        # Get the resulting type of an operation between two types
        for cur_type in [type1, type2]:
            if cur_type not in self.cube:
                raise ValueError(f"Invalid type: {cur_type}. Expected 'int' or 'float'.")
        
        if operation not in self.cube[type1][type2]:
            raise ValueError(f"Operation {operation} not valid for types {type1} and {type2}.")

        return self.cube[type1][type2][operation]
    
    def perform_operation(self, left_value: Union[float, int], right_value: Union[float, int], operation) -> int | float:
        """
        Perform the operation between two values.
        
        Args:
            left_value: The left operand value
            right_value: The right operand value
            operation: The operation to perform ('+', '-', '*', '/', '<', '>', '!=')
            
        Returns:
            tuple: (result_value, result_type)
        """

        left_type = type(left_value).__name__
        right_type = type(right_value).__name__
        
        # First check if the operation is valid for these types
        result_type = self.get_resulting_type(left_type, right_type, operation)
        
        # Perform the operation
        if operation == "+":
            result = left_value + right_value
        elif operation == "-":
            result = left_value - right_value
        elif operation == "*":
            result = left_value * right_value
        elif operation == "/":
            if right_value == 0:
                raise ValueError("Division by zero")
            result = left_value / right_value
        elif operation == "<":
            result = 1 if left_value < right_value else 0
        elif operation == ">":
            result = 1 if left_value > right_value else 0
        elif operation == "!=":
            result = 1 if left_value != right_value else 0
        else:
            raise ValueError(f"Unsupported operation: {operation}")
            
        # Convert the result if needed
        if result_type == "int" and not isinstance(result, int):
            result = int(result)
        if result_type == "float" and not isinstance(result, float):
            result = float(result)
        
        return result
        
    def is_decl_valid(self, from_type, to_type):
        # Check if the types are valid for declaration
        for cur_type in [from_type, to_type]:
            if cur_type not in self.valid_declarations:
                raise ValueError(f"Invalid type: {cur_type}. Expected 'int' or 'float'.")
        return (to_type in self.valid_declarations[from_type])
    
    def convert_type(self, from_type, to_type, value):
        # Convert value from type1 to type2 if valid
        if not self.is_decl_valid(to_type, from_type):
            raise ValueError("Invalid declaration: types not compatible")
            
        return self.valid_declarations[to_type][from_type](value)
        
        