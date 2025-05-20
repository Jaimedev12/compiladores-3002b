from ast import Pass
from dataclasses import dataclass
from turtle import left
from typing import cast, List, Union, Tuple, Optional
from SemanticCube import SemanticCube
from node_dataclasses import *
from SymbolTable import SymbolTable
from MemoryManager import AllocCategory, Operations, MemoryManager
# from lark import Tree

class BabyInterpreter:
    def __init__(self, symbol_table: SymbolTable, memory_manager: MemoryManager):
        self.symbol_table = symbol_table
        self.current_scope = "global"
        self.semantic_cube = SemanticCube()
        self.quads: List[Quad] = []
        self.memory_manager = memory_manager

    def add_quad(
            self, 
            op: Operations, 
            vdir1: int, 
            vdir2: Optional[int] = None, 
            storage_vdir: Optional[int] = None,
            ) -> Quad:
        """Add a quadruple to the list of quads."""

        quad = Quad(op_vdir=op.value, vdir1=vdir1, vdir2=vdir2, storage_vdir=storage_vdir, scope=self.current_scope)
        self.quads.append(quad)
        return quad

    def evaluate_expression(self, current_tree_node) -> int:
        if isinstance(current_tree_node, Expression):
            left_vdir = self.evaluate_expression(current_tree_node.left_expr)

            if current_tree_node.op is None or current_tree_node.right_expr is None:
                return left_vdir
            
            right_vdir = self.evaluate_expression(current_tree_node.right_expr)
    
            op = current_tree_node.op
            alloc_vdir = self.memory_manager.allocate(AllocCategory.TEMP_INT)
            quad = self.add_quad(op=op, vdir1=left_vdir, vdir2=right_vdir, storage_vdir=alloc_vdir)
            assert quad.storage_vdir is not None, "Quadruple storage_vdir should not be None"
            return quad.storage_vdir
            
        
        elif isinstance(current_tree_node, Exp):
            left_vdir = self.evaluate_expression(current_tree_node.left_term)
            for op, term in current_tree_node.operations:
                right_vdir = self.evaluate_expression(term)

                left_vdir_type = self.memory_manager.get_address_type(left_vdir)
                right_vdir_type = self.memory_manager.get_address_type(right_vdir)

                result_type = self.semantic_cube.get_resulting_type(
                    left_vdir_type, right_vdir_type, op
                )

                storage_vdir = self.memory_manager.allocate(
                    AllocCategory.TEMP_INT if result_type == "int" else AllocCategory.TEMP_FLOAT,
                )
                quad = self.add_quad(
                    op=op, 
                    vdir1=left_vdir, 
                    vdir2=right_vdir,
                    storage_vdir=storage_vdir
                    )
                left_vdir = storage_vdir
            return left_vdir
        
        elif isinstance(current_tree_node, Term):
            left_vdir = self.evaluate_expression(current_tree_node.left_factor)
            for op, factor in current_tree_node.operations:
                right_vdir = self.evaluate_expression(factor)

                left_vdir_type = self.memory_manager.get_address_type(left_vdir)
                right_vdir_type = self.memory_manager.get_address_type(right_vdir)

                result_type = self.semantic_cube.get_resulting_type(
                    left_vdir_type, right_vdir_type, op
                )

                storage_vdir = self.memory_manager.allocate(
                    AllocCategory.TEMP_INT if result_type == "int" else AllocCategory.TEMP_FLOAT,
                )
                quad = self.add_quad(
                    op=op, 
                    vdir1=left_vdir, 
                    vdir2=right_vdir,
                    storage_vdir=storage_vdir
                    )
                left_vdir = storage_vdir
            return left_vdir
        
        elif isinstance(current_tree_node, Factor):
            if isinstance(current_tree_node.value, str):
                # Check if the value is a variable
                if not self.symbol_table.is_symbol_declared(current_tree_node.value, self.current_scope):
                    raise ValueError(f"Variable {current_tree_node.value} is not declared.")
                
                symbol = self.symbol_table.get_symbol(
                    current_tree_node.value, 
                    self.current_scope,
                )
                return symbol.vdir # Stored in the symbol table                    

            elif isinstance(current_tree_node.value, (int, float)):
                if current_tree_node.sign == '-':
                    value = current_tree_node.value * -1
                else:
                    value = current_tree_node.value
                    
                vdir = self.memory_manager.allocate(AllocCategory.CONSTANT, const_value=value)
                return vdir
                
            elif isinstance(current_tree_node.value, Expression):
                return self.evaluate_expression(current_tree_node.value)
            
            else:
                raise ValueError(f"Unsupported factor type: {type(current_tree_node.value)}")
        
        else :
            raise ValueError(f"Unsupported expression type: {current_tree_node.__class__.__name__}")
    
    
    def generate_quads(self, ir):    
        if isinstance(ir, Program): 
            self.gen_quads_program(ir)

        elif isinstance(ir, Vars):
            self.gen_quads_vars(ir)

        elif isinstance(ir, VarDeclaration):
            self.gen_quads_var_declaration(ir)

        elif isinstance(ir, Function):
            self.gen_quads_function(ir)

        elif isinstance(ir, Assign):
            self.gen_quads_assign(ir)

        elif isinstance(ir, Print):
            self.gen_quads_print(ir)

        elif isinstance(ir, Condition):
            self.gen_quads_condition(ir)

        elif isinstance(ir, Cycle):
            self.gen_quads_cycle(ir)

        elif isinstance(ir, Body):
            self.gen_quads_body(ir)

        elif isinstance(ir, FCall):
            self.gen_quads_f_call(ir)

    
    def gen_quads_program(self, ir: Program):
        if ir.vars is not None: 
            self.gen_quads_vars(ir.vars)
        for func in ir.funcs:
            self.gen_quads_function(func)
        self.gen_quads_body(ir.body)

    def gen_quads_vars(self, ir: Vars): 
        for var_decl in ir.declarations:
            self.gen_quads_var_declaration(var_decl)

    def gen_quads_var_declaration(self, ir: VarDeclaration): 
        for var_name in ir.names:
            vdir = self.symbol_table.add_symbol_by_attrs(
                name=var_name,
                data_type=ir.type_,
                scope_name=self.current_scope,
                value=None
            )
            self.add_quad(op=Operations.ASSIGN, vdir1=vdir)

    def gen_quads_function(self, ir: Function): 
        self.current_scope = ir.id
        self.symbol_table.add_function(name=ir.id, params=ir.params, body=ir.body)
        if ir.vars is not None: 
            self.gen_quads_vars(ir.vars)
        self.gen_quads_body(ir.body)
        self.current_scope = "global"

    def gen_quads_assign(self, ir: Assign): 
        expr_vdir = self.evaluate_expression(ir.expr)
        expr_type = self.memory_manager.get_address_type(expr_vdir)

        if not self.symbol_table.is_symbol_declared(ir.id, self.current_scope):
            raise ValueError(f"Variable {ir.id} is not declared.")
        
        symbol = self.symbol_table.get_symbol(ir.id, self.current_scope)
        var_type = symbol.data_type
        is_valid_decl = self.semantic_cube.is_decl_valid(from_type=expr_type, to_type=var_type)
        if not is_valid_decl:
            raise ValueError(f"Invalid assignment: {expr_type} cannot be assigned to {var_type}.")
        
        self.add_quad(op=Operations.ASSIGN, vdir1=symbol.vdir, vdir2=expr_vdir)

    def gen_quads_print(self, ir: Print): 
        for content in ir.contents:
            if isinstance(content, str):
                allocated_const = self.memory_manager.allocate(AllocCategory.CONSTANT, const_value=content)
                self.add_quad(op=Operations.PRINT, vdir1=allocated_const)
            else:
                # Evaluate the expression and print its value
                expr_vdir = self.evaluate_expression(content)
                self.add_quad(op=Operations.PRINT, vdir1=expr_vdir)
        print()  # New line after printing all contents

    def gen_quads_condition(self, ir: Condition): 
        pass

    def gen_quads_cycle(self, ir: Cycle): 
        pass

    def gen_quads_body(self, ir: Body): 
        for statement in ir.statements:
            self.generate_quads(statement)

    def gen_quads_f_call(self, ir: FCall): 
        self.current_scope = ir.id
        # Check if function is declared
        if not self.symbol_table.is_function_declared(ir.id):
            raise ValueError(f"Function {ir.id} is not declared.")
            
        self.current_scope = "global"

        pass
