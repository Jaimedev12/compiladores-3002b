import pickle
import sys
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Import the same dataclasses to ensure compatibility
from util_dataclasses import Quad, ConstantValue
from SymbolTable import Scope
from gen_obj import ObjectFileMetadata, ObjData

def read_obj_file(obj_path: str) -> ObjData:
    try:
        with open(obj_path, 'rb') as file:
            obj_data = pickle.load(file)
            return obj_data
    except FileNotFoundError:
        print(f"Error: Object file '{obj_path}' not found")
        sys.exit(1)
    except pickle.UnpicklingError:
        print(f"Error: '{obj_path}' is not a valid BabyDuck object file")
        sys.exit(1)

def display_obj_info(obj_data: ObjData):
    print("===== BabyDuck Object File =====")
    print(f"Program: {obj_data.metadata.filename}")
    print(f"Compiled: {obj_data.metadata.timestamp}")
    print()
    
    # Display constants
    print("===== Constants Table =====")
    for addr, value in obj_data.constants.items():
        value_str = repr(value)
        print(f"[{addr}] = {value_str}")
    print()
    
    # Display functions/scopes
    print("===== Function Directory =====")
    for name, scope in obj_data.functions.items():
        if name == "global":
            print(f"Global Scope: {len(scope.symbols)} symbols")
        else:
            print(f"Function: {name}")
            print(f"  Parameters: {len(scope.param_list)}")
            print(f"  Local Variables: {len(scope.symbols) - len(scope.param_list)}")
    print()
    
    # Display quads
    print("===== Quadruples =====")
    for i, quad in enumerate(obj_data.quads):
        quad_str = f"{i}: {quad.op_vdir}"
        
        if quad.vdir1 is not None:
            quad_str += f" {quad.vdir1}"
            
        if quad.vdir2 is not None:
            quad_str += f" {quad.vdir2}"
            
        if quad.storage_vdir is not None:
            quad_str += f" -> {quad.storage_vdir}"
            
        if quad.label is not None:
            quad_str += f" [{quad.label}]"
            
        print(quad_str)

def main():

    obj_file_path = "output/function.obj"

    if len(sys.argv) == 2:
        obj_file_path = sys.argv[1]
        if not obj_file_path.endswith('.obj'):
            obj_file_path += '.obj'

    obj_data = read_obj_file(obj_file_path)
    display_obj_info(obj_data)

    # You could also implement a virtual machine here to execute the bytecode
    print("\nTo run this program, use baby_vm.py")

if __name__ == "__main__":
    main()