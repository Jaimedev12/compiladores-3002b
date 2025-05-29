from dataclasses import dataclass
from datetime import datetime
import sys
import pickle
import os
import contextlib
from lark import Lark
from BabyTransformer import BabyTransformer
from BabyInterpreter import BabyInterpreter
from SymbolTable import SymbolTable, Scope
from MemoryManager import MemoryManager
from typing import Dict, List

from custom_classes.values import ConstantValue
from custom_classes.memory import Operations, AllocCategory
from custom_classes.classes import Quad

    
@dataclass
class ObjectFileMetadata:
    filename: str
    timestamp: str

@dataclass
class ObjData:
    metadata: ObjectFileMetadata
    constants: Dict[int, ConstantValue]
    functions: Dict[str, Scope]
    size_per_local: Dict[str, Dict[AllocCategory, int]]
    quads: List[Quad]


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
    

def gen_obj(file_path: str, filename: str, output_path: str = "./output") -> None:

    with open('grammar.lark', 'r') as file:
        grammar = file.read()

    babyParser = Lark(grammar, start='start', parser='lalr', debug=True)
    baby = babyParser.parse

    babyParser = Lark(grammar, start='start', parser='lalr', debug=True)
    baby = babyParser.parse

    # tests_dir = "./input"
    output_dir = "./output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = os.path.splitext(filename)[0]
    input_filename = file_path + os.sep + filename
    output_filename = output_dir + os.sep + f"{base_name}.ovejota"
    output_object_filename = output_dir + os.sep + f"{base_name}.obj"

    with open(output_filename, 'w', encoding='utf-8') as output_file:
        with contextlib.redirect_stdout(output_file):
            with open(input_filename, 'r', encoding='utf-8') as input_file:
                program = input_file.read()
                memory_manager = MemoryManager()

                symbol_table = SymbolTable(memory_manager=memory_manager)
                tree = baby(program)

                baby_transformer = BabyTransformer()
                ir = baby_transformer.transform(tree)

                baby_interpreter = BabyInterpreter(symbol_table, memory_manager=memory_manager)
                baby_interpreter.generate_quads(ir)

                output_file.write(f"# BabyDuck Object File: {base_name}\n")
                output_file.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                output_file.write("# Constants Table\n")
                for addr, const_value in memory_manager.constants.items():
                    output_file.write(f"{addr} {repr(const_value)}\n")
                output_file.write("\n")
                
                output_file.write("# Function Directory\n")
                output_file.write(symbol_table.to_string())
                output_file.write("\n")

                output_file.write("# Memory Manager\n")
                output_file.write(symbol_table.memory_manager.to_string())
                output_file.write("\n")
                
                output_file.write("# Quadruples\n")
                for i, quad in enumerate(baby_interpreter.quads):
                    output_file.write(f"<{i}> {quad.op_vdir} {quad.vdir1} {quad.vdir2} {quad.storage_vdir}")
                    if quad.label:
                        output_file.write(f" -> {quad.label}")
                    output_file.write("\n")

                output_file.write("--------\n")

                for i, quad in enumerate(baby_interpreter.quads):
                    output_file.write(f"<{i}> {str(Operations(quad.op_vdir))[11:]}")
                    if quad.vdir1:
                        if quad.op_vdir == Operations.GOTO.value or quad.op_vdir == Operations.GOSUB.value:
                            output_file.write(f" {quad.vdir1}")
                        else:
                            output_file.write(f" {get_symbol_name(symbol_table, memory_manager, vdir=quad.vdir1, scope_name=quad.scope)}")
                    if quad.vdir2:
                        if quad.op_vdir == Operations.GOTOF.value:
                            output_file.write(f" {quad.vdir2}")
                        else:
                            output_file.write(f" {get_symbol_name(symbol_table, memory_manager, vdir=quad.vdir2, scope_name=quad.scope)}")

                    if quad.storage_vdir:
                        output_file.write(f" {get_symbol_name(symbol_table, memory_manager, vdir=quad.storage_vdir, scope_name=quad.scope)}")
                    
                    if quad.label:
                        output_file.write(f" -> {quad.label}")

                    output_file.write("\n")

                with open(output_object_filename, 'wb') as binary_output:
                    obj_data = ObjData(
                        metadata=ObjectFileMetadata(
                            filename=base_name,
                            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ),
                        constants=memory_manager.constants,
                        functions=symbol_table.scopes,
                        quads=baby_interpreter.quads,
                        size_per_local=symbol_table.memory_manager.size_per_local
                    )
                    pickle.dump(obj_data, binary_output)


        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    gen_obj("./input", "function.baby")