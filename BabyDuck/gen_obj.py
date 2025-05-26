from datetime import datetime
import sys
import pickle
import os
import contextlib
from lark import Lark, UnexpectedInput
from BabyTransformer import BabyTransformer
from BabyInterpreter import BabyInterpreter
from SymbolTable import SymbolTable
from MemoryManager import MemoryManager, Operations, AllocCategory

    
# Parse command-line arguments
# parser = argparse.ArgumentParser(description="Run a BabyScript program.")
# parser.add_argument("input_file", help="Path to the BabyScript input file")
# args = parser.parse_args()

# Import grammar from file
with open('grammar.lark', 'r') as file:
    grammar = file.read()


def get_symbol_name(symbol_table: SymbolTable, mem_mgr: MemoryManager, vdir: int, scope_name: str = "global") -> str:
    if vdir < mem_mgr.address_ranges[AllocCategory.GLOBAL_INT].start:
        raise ValueError("Invalid variable directory (vdir)")
    if vdir < mem_mgr.address_ranges[AllocCategory.TEMP_INT].start:
        return symbol_table.get_symbol(vdir, scope_name=scope_name).name
    if vdir <= mem_mgr.address_ranges[AllocCategory.TEMP_INT].end:
        return "ti"+str(vdir-mem_mgr.address_ranges[AllocCategory.TEMP_INT].start)
    if vdir <= mem_mgr.address_ranges[AllocCategory.TEMP_FLOAT].end:
        return "tf"+str(vdir-mem_mgr.address_ranges[AllocCategory.TEMP_FLOAT].start)
    else:
        return str(mem_mgr.constants[vdir])
    

def gen_obj():

    with open('grammar.lark', 'r') as file:
        grammar = file.read()

    # Create the Lark parser
    babyParser = Lark(grammar, start='start', parser='lalr', debug=True)
    baby = babyParser.parse

    
    # Create the Lark parser
    babyParser = Lark(grammar, start='start', parser='lalr', debug=True)
    baby = babyParser.parse

    tests_dir = "./input"
    output_dir = "./output"

    if not os.path.exists(tests_dir):
        os.makedirs(tests_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(tests_dir):
        if not filename.endswith(".baby"):
            continue

        base_name = os.path.splitext(filename)[0]
        input_filename = os.path.join(tests_dir, filename)
        output_filename = os.path.join(output_dir, f"{base_name}.ovejota")
        output_object_filename = os.path.join(output_dir, f"{base_name}.obj")

        with open(output_filename, 'w', encoding='utf-8') as output_file:
            with contextlib.redirect_stdout(output_file):
                with open(input_filename, 'r', encoding='utf-8') as input_file:
                    program = input_file.read()
                    memory_manager = MemoryManager()

                    # Initialize the symbol table
                    symbol_table = SymbolTable(memory_manager=memory_manager)
                    tree = baby(program)
                    # print(tree.pretty())

                    # Transform the parse tree using BabyTransformer
                    baby_transformer = BabyTransformer()
                    ir = baby_transformer.transform(tree)
                    # print(ir)

                    # Execute the IR
                    baby_interpreter = BabyInterpreter(symbol_table, memory_manager=memory_manager)
                    baby_interpreter.generate_quads(ir)

                    # Generate object file content
                    output_file.write(f"# BabyDuck Object File: {base_name}\n")
                    output_file.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    # Write constants table
                    output_file.write("# Constants Table\n")
                    for addr, const_value in memory_manager.constants.items():
                        output_file.write(f"{addr} {repr(const_value)}\n")
                    output_file.write("\n")
                    
                    # Write function directory
                    output_file.write("# Function Directory\n")
                    for scope_name, scope in symbol_table.scopes.items():
                        if scope_name != "global":
                            output_file.write(f"FUNC {scope_name}\n")
                    output_file.write("\n")
                    
                    # Write quads
                    output_file.write("# Quadruples\n")
                    for i, quad in enumerate(baby_interpreter.quads):
                        quad_str = f"{i} {quad.op_vdir}"

                        if quad.vdir1 is not None:
                            quad_str += f" {quad.vdir1}"

                        if quad.vdir2 is not None:
                            quad_str += f" {quad.vdir2}"

                        if quad.storage_vdir is not None:
                            quad_str += f" {quad.storage_vdir}"
                        
                        if quad.label is not None:
                            quad_str += f" -> {quad.label}"

                        output_file.write(quad_str + "\n")

                    print(f"Successfully compiled {filename} to {base_name}.ovejota")

                    with open(output_object_filename, 'wb') as output_file:
                        obj_data = {
                            'metadata': {
                                'filename': base_name,
                                'timestamp': datetime.now().isoformat(),
                            },
                            'constants': memory_manager.constants,
                            'functions': {name: scope.__dict__ for name, scope in symbol_table.scopes.items()},
                            'quads': [quad.__dict__ for quad in baby_interpreter.quads],
                        }
                        pickle.dump(obj_data, output_file)


        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    gen_obj()