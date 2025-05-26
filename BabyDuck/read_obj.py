import pickle
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

def load_object_file(obj_file_path: str) -> Dict[str, Any]:
    """
    Load a compiled BabyDuck object file.
    
    Args:
        obj_file_path: Path to the .obj file
        
    Returns:
        Dictionary containing the object file data
    """
    try:
        with open(obj_file_path, 'rb') as file:
            obj_data = pickle.load(file)
            return obj_data
    except FileNotFoundError:
        print(f"Error: Object file '{obj_file_path}' not found.")
        sys.exit(1)
    except pickle.UnpicklingError:
        print(f"Error: '{obj_file_path}' is not a valid BabyDuck object file.")
        sys.exit(1)

def print_obj_info(obj_data: Dict[str, Any]) -> None:
    """Print information about the loaded object file."""
    metadata = obj_data.get('metadata', {})
    
    print("BABYDUCK OBJECT FILE")
    print("===================")
    print(f"Filename: {metadata.get('filename', 'Unknown')}")
    print(f"Compiled on: {metadata.get('timestamp', 'Unknown')}")
    print()
    
    # Print constants
    print("CONSTANTS TABLE")
    print("==============")
    constants = obj_data.get('constants', {})
    for addr, value in constants.items():
        print(f"[{addr}] = {repr(value)}")
    print()
    
    # Print functions
    print("FUNCTION DIRECTORY")
    print("=================")
    functions = obj_data.get('functions', {})
    for func_name, func_data in functions.items():
        if func_name == "global":
            continue
        print(f"Function: {func_name}")
        if 'params' in func_data:
            print(f"  Parameters: {len(func_data['params'])}")
    print()
    
    # Print quads
    print("QUADRUPLES")
    print("==========")
    quads = obj_data.get('quads', [])
    for i, quad in enumerate(quads):
        op = quad.get('op_vdir', '?')
        vdir1 = quad.get('vdir1', None)
        vdir2 = quad.get('vdir2', None)
        storage_vdir = quad.get('storage_vdir', None)
        label = quad.get('label', None)
        
        quad_str = f"{i}: {op}"
        if vdir1 is not None:
            quad_str += f" {vdir1}"
        if vdir2 is not None:
            quad_str += f" {vdir2}"
        if storage_vdir is not None:
            quad_str += f" -> {storage_vdir}"
        if label is not None:
            quad_str += f" [{label}]"
            
        print(quad_str)

def main():

    obj_file_path = "output/function.obj"

    if len(sys.argv) == 2:
        obj_file_path = sys.argv[1]

    obj_data = load_object_file(obj_file_path)
    print_obj_info(obj_data)
    
    # You could also implement a virtual machine here to execute the bytecode
    print("\nTo run this program, use baby_vm.py")

if __name__ == "__main__":
    main()