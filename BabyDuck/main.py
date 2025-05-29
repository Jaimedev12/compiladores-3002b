#!/usr/bin/env python3
import os
import sys
import pickle
from datetime import datetime

from lark import Lark
from BabyTransformer import BabyTransformer
from BabyInterpreter import BabyInterpreter
from SymbolTable import SymbolTable
from MemoryManager import MemoryManager
from BabyVirtualMachine import BabyVirtualMachine
from gen_obj import ObjectFileMetadata, ObjData, gen_obj
from read_obj import read_obj_file

def compile_and_run(file_path: str, filename: str):
    """
    Compiles a BabyDuck file and runs it immediately
    
    Args:
        input_file: Path to the .baby source file
    """

    gen_obj(file_path, filename+".baby")
    # Setup output paths
    obj_data = read_obj_file("output/" + filename+".obj")

    try:
        # Run the program
        print("\nRunning program...")
        print("-" * 40)
        vm = BabyVirtualMachine(obj_data)
        vm.run()
        print("\n" + "-" * 40)
        print("Program execution completed")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.baby>")
        sys.exit(1)
    
    input_path = "./input"
    # filename = "function.baby"
    filename = sys.argv[1]
    input_file = os.path.join(input_path, filename)

        
    compile_and_run(input_path, filename)