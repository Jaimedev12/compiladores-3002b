import logging
import sys
import os
import contextlib
from lark import Lark, logger, UnexpectedInput
from BabyTransformer import BabyTransformer
from BabyInterpreter import BabyInterpreter
from SymbolTable import SymbolTable
from vdir_classes import MemoryManager
from vdir_classes import VariableType, Operations

logger.setLevel(logging.DEBUG)

# Parse command-line arguments
# parser = argparse.ArgumentParser(description="Run a BabyScript program.")
# parser.add_argument("input_file", help="Path to the BabyScript input file")
# args = parser.parse_args()

# Import grammar from file
with open('grammar.lark', 'r') as file:
    grammar = file.read()

# Create the Lark parser
babyParser = Lark(grammar, start='start', parser='lalr', debug=True)
baby = babyParser.parse

def get_symbol_name(symbol_table: SymbolTable, memory_manager: MemoryManager, vdir: int) -> str:
    """
    Get the symbol information from the symbol table and memory manager.
    """

    if vdir < 1000:
        raise ValueError("Invalid variable directory (vdir)")
    if vdir < 5000:
        # Global Int
        return symbol_table.get_variable(vdir).name
    if vdir < 6000:
        return "ti"+str(vdir-5000)
        # Temp Int
    if vdir < 7000:
        return "tf"+str(vdir-6000)
    else:
        return str(memory_manager.constants[vdir])

    

def parse_code(input_code, memory_manager: MemoryManager, symbol_table: SymbolTable):
    try:

        # Parse the input code
        tree = baby(input_code)
        # print(tree.pretty())

        # Transform the parse tree using BabyTransformer
        baby_transformer = BabyTransformer()
        ir = baby_transformer.transform(tree)
        # print(ir)

        # Execute the IR
        baby_interpreter = BabyInterpreter(symbol_table, memory_manager=memory_manager)
        baby_interpreter.execute(ir)

        # Display the symbol table after execution
        # print("\nSymbol Table after execution:")
        # symbol_table.display()

        return (tree.pretty(), ir, symbol_table.to_string(), baby_interpreter.quads)
    except UnexpectedInput as e:
        print(f"Parsing failed: {e}")
        raise e  # Re-raise the exception for further handling

if __name__ == "__main__":
    # Toma todos los archivos de la carpeta ./tests, realiza el parseo y guarda
    # el output en un archivo .out por cada uno de los archivos .baby
    # en la carpeta ./output
    tests_dir = "./debug"
    output_dir = "./output"

    if not os.path.exists(tests_dir):
        os.makedirs(tests_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(tests_dir):
        if not filename.endswith(".baby"):
            continue

        base_name = os.path.splitext(filename)[0]
        log_filename = os.path.join(output_dir, f"{base_name}.log")
        input_filename = os.path.join(tests_dir, filename)
        output_filename = os.path.join(output_dir, f"{base_name}.out")
        
        memory_manager = MemoryManager()

        # Initialize the symbol table
        symbol_table = SymbolTable(memory_manager=memory_manager)

        with open(log_filename, "w", encoding="utf-8") as log_file:
            with contextlib.redirect_stdout(log_file):
                with open(input_filename, 'r', encoding='utf-8') as input_file:
                    program = input_file.read()
                    tree, ir, symbol_table_string, quads = parse_code(program, memory_manager=memory_manager, symbol_table=symbol_table)
                
                with open(output_filename, 'w', encoding='utf-8') as output_file:
                    output_file.write("Parse Tree:\n")
                    output_file.write(str(tree))
                    output_file.write("\nIR:\n")
                    output_file.write(str(ir))
                    output_file.write("\n\nSymbol Table:\n")
                    output_file.write(symbol_table_string)
                    output_file.write("\n")
                    output_file.write("\nQuads:\n")
                    for quad in quads:
                        output_file.write(f"{quad.op_vdir} {quad.vdir1} {quad.vdir1} {quad.storage_vdir}")
                        if quad.label:
                            output_file.write(f" -> {quad.label}")
                        output_file.write("\n")
                    output_file.write("--------\n")
                    for quad in quads:
                        output_file.write(f"{Operations(quad.op_vdir)}")
                        if quad.vdir1:
                            output_file.write(f" {get_symbol_name(symbol_table, memory_manager, quad.vdir1)}")
                        
                        if quad.vdir2:
                            output_file.write(f" {get_symbol_name(symbol_table, memory_manager, vdir=quad.vdir2)}")

                        if quad.storage_vdir:
                            output_file.write(f" {get_symbol_name(symbol_table, memory_manager, vdir=quad.storage_vdir)}")
                        
                        if quad.label:
                            output_file.write(f" -> {quad.label}")
                        output_file.write("\n")
                    output_file.write("\n")

                    

        sys.stdout = sys.__stdout__
    # Si se pasa un archivo como argumento, lo parsea y ejecuta
    # el programa, mostrando el resultado en la consola
    # if args.input_file:
    #     # clear console
    #     print("\033[H\033[J", end="")
    #     # Parse the input program
    #     with open(args.input_file, 'r') as input_file:
    #         program = input_file.read()
    #         parse_code(program)

    