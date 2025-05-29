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

def compile_and_run(file_path: str, filename: str):
    """
    Compiles a BabyDuck file and runs it immediately
    
    Args:
        input_file: Path to the .baby source file
    """

    gen_obj(file_path, filename)
    # Setup output paths
    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_dir = os.path.dirname(file_path)
    output_object_filename = os.path.join(output_dir, f"{base_name}.obj")
    
    print(f"Compiling {input_file}...")
    
    # Load grammar
    with open('grammar.lark', 'r') as file:
        grammar = file.read()
    
    # Create parser
    parser = Lark(grammar, start='start', parser='lalr')
    
    # Compile
    try:
        # Read program
        with open(input_file, 'r', encoding='utf-8') as source_file:
            program = source_file.read()
        
        # Setup core components
        memory_manager = MemoryManager()
        symbol_table = SymbolTable(memory_manager=memory_manager)
        
        # Parse to AST
        tree = parser.parse(program)
        
        # Transform to IR
        baby_transformer = BabyTransformer()
        ir = baby_transformer.transform(tree)
        
        # Generate quads
        baby_interpreter = BabyInterpreter(symbol_table, memory_manager=memory_manager)
        baby_interpreter.generate_quads(ir)
        
        # Create binary object file
        obj_data = ObjData(
            metadata=ObjectFileMetadata(
                filename=base_name,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ),
            constants=memory_manager.constants,
            functions=symbol_table.scopes,
            quads=baby_interpreter.quads
        )
        
        # Save object file
        with open(output_object_filename, 'wb') as binary_output:
            pickle.dump(obj_data, binary_output)
            
        print(f"Compilation successful. Object file: {output_object_filename}")
        
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
    if not input_file.endswith('.baby'):
        print("File must have .baby extension")
        sys.exit(1)
        
    compile_and_run(input_path, filename)