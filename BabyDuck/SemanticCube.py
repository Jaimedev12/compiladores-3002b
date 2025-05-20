from typing import Union, cast
from webbrowser import Opera
from node_dataclasses import *
from MemoryManager import *

class SemanticCube:
    def __init__(self):
        self.cube = {
            "int": {
                "int": {
                    Operations.PLUS: "int",
                    Operations.MINUS: "int",
                    Operations.MULT: "int",
                    Operations.DIV: "int",
                    Operations.LESS_THAN: "int",
                    Operations.GREATER_THAN: "int",
                    Operations.NOT_EQUAL: "int",
                },
                "float": {
                    Operations.PLUS: "float",
                    Operations.MINUS: "float",
                    Operations.MULT: "float",
                    Operations.DIV: "float",
                    Operations.LESS_THAN: "int",
                    Operations.GREATER_THAN: "int",
                    Operations.NOT_EQUAL: "int",
                }
            },
            "float": {
                "int": {
                    Operations.PLUS: "float",
                    Operations.MINUS: "float",
                    Operations.MULT: "float",
                    Operations.DIV: "float",
                    Operations.LESS_THAN: "int",
                    Operations.GREATER_THAN: "int",
                    Operations.NOT_EQUAL: "int",
                },
                "float": {
                    Operations.PLUS: "float",
                    Operations.MINUS: "float",
                    Operations.MULT: "float",
                    Operations.DIV: "float",
                    Operations.LESS_THAN: "int",
                    Operations.GREATER_THAN: "int",
                    Operations.NOT_EQUAL: "int",
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

    def get_resulting_type(self, type1: ValueType, type2: ValueType, operation: Operations) -> ValueType:
        # Get the resulting type of an operation between two types
        for cur_type in [type1, type2]:
            if cur_type not in self.cube:
                raise ValueError(f"Invalid type: {cur_type}. Expected 'int' or 'float'.")
        
        if operation not in self.cube[type1][type2]:
            raise ValueError(f"Operation {operation} not valid for types {type1} and {type2}.")

        assert self.cube[type1][type2][operation] in ["int", "float", "str"], f"Expected 'int', 'float', or 'str', but got {self.cube[type1][type2][operation]!r}"
        return cast(ValueType, self.cube[type1][type2][operation])
            
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
        
        