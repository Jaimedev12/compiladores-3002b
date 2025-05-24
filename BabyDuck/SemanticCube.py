from typing import Union, cast
from webbrowser import Opera
from node_dataclasses import *
from MemoryManager import *

class SemanticCube:
    def __init__(self):
        self.cube: Dict[str, Dict[str, Dict[Operations, VariableType]]] = {
            "int": {
                "int": {
                    Operations.ASSIGN: "int",
                    Operations.PLUS: "int",
                    Operations.MINUS: "int",
                    Operations.MULT: "int",
                    Operations.DIV: "int",
                    Operations.LESS_THAN: "int",
                    Operations.GREATER_THAN: "int",
                    Operations.NOT_EQUAL: "int",
                },
                "float": {
                    Operations.ASSIGN: "int",
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
                    Operations.ASSIGN: "float",
                    Operations.PLUS: "float",
                    Operations.MINUS: "float",
                    Operations.MULT: "float",
                    Operations.DIV: "float",
                    Operations.LESS_THAN: "int",
                    Operations.GREATER_THAN: "int",
                    Operations.NOT_EQUAL: "int",
                },
                "float": {
                    Operations.ASSIGN: "float",
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


    def get_resulting_type(self, type1: ValueType, type2: ValueType, operation: Operations) -> ValueType:
        for cur_type in [type1, type2]:
            if cur_type not in self.cube:
                raise ValueError(f"Invalid type: {cur_type}. Expected 'int' or 'float'.")
        
        if operation not in self.cube[type1][type2]:
            raise ValueError(f"Operation {operation} not valid for types {type1} and {type2}.")

        return self.cube[type1][type2][operation]
            
    def is_decl_valid(self, from_type, to_type):
        # Check if the types are valid for declaration
        if self.cube[from_type][to_type][Operations.ASSIGN] is None:
            return False
        return True
    
        
        