from typing import List, Optional
from SemanticCube import SemanticCube
from node_dataclasses import *
from SymbolTable import SymbolTable
from MemoryManager import AllocCategory, Operations, MemoryManager
from FunctionTable import FunctionTable
# from lark import Tree

class BabyInterpreter:
    def __init__(self, symbol_table: SymbolTable, memory_manager: MemoryManager):
        self.symbol_table = symbol_table
        self.current_scope = "global"
        self.semantic_cube = SemanticCube()
        self.quads: List[Quad] = []
        self.memory_manager = memory_manager
        self.function_table = FunctionTable(memory_manager=memory_manager)

    def add_quad(
            self, 
            op: Operations, 
            vdir1: Optional[int] = None, 
            vdir2: Optional[int] = None, 
            storage_vdir: Optional[int] = None,
            label: Optional[str] = None,
            ) -> Quad:
        """Add a quadruple to the list of quads."""

        quad = Quad(op_vdir=op.value, vdir1=vdir1, vdir2=vdir2, storage_vdir=storage_vdir, scope=self.current_scope, label=label)
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
        self.add_quad(op=Operations.GOTO, vdir1=-1)
        main_goto_pos = len(self.quads) - 1
        if ir.vars is not None: 
            self.gen_quads_vars(ir.vars)
        for func in ir.funcs:
            self.gen_quads_function(func)
        self.quads[main_goto_pos].vdir1 = len(self.quads)
        self.gen_quads_body(ir.body)
        self.add_quad(op=Operations.END)

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
            # self.add_quad(op=Operations.ASSIGN, vdir1=vdir)

    def gen_quads_function(self, ir: Function): 
        self.current_scope = ir.id
        self.symbol_table.add_function(name=ir.id, params=ir.params, body=ir.body)
        self.function_table.add_function(ir, start_quad=len(self.quads))
        if ir.vars is not None: 
            self.gen_quads_vars(ir.vars)
        self.gen_quads_body(ir.body)
        
        self.function_table.update_allocation_tracker(name=ir.id)
        self.current_scope = "global"
        self.add_quad(op=Operations.ENDFUNC)

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
        expr_vdir = self.evaluate_expression(ir.expr)
        expr_type = self.memory_manager.get_address_type(expr_vdir)
        if expr_type != "int":
            raise ValueError(f"Condition expression must be of type int, got {expr_type}.")
        
        self.add_quad(op=Operations.GOTOF, vdir1=expr_vdir)
        gotof_pos = len(self.quads) - 1
        
        self.gen_quads_body(ir.if_body)
        
        if ir.else_body is not None:
            self.add_quad(op=Operations.GOTO, vdir1=-1)
            goto_quad_pos = len(self.quads) - 1

            self.gen_quads_body(ir.else_body)
            self.quads[goto_quad_pos].vdir1 = len(self.quads)
        
        self.quads[gotof_pos].vdir2 = len(self.quads)

    def gen_quads_cycle(self, ir: Cycle): 
        quad_pos_bef_eval = len(self.quads)
        expr_vdir = self.evaluate_expression(ir.expr)
        expr_type = self.memory_manager.get_address_type(expr_vdir)
        if expr_type != "int":
            raise ValueError(f"Condition expression must be of type int, got {expr_type}.")
        
        self.add_quad(op=Operations.GOTOF, vdir1=expr_vdir)
        open_pos = len(self.quads) - 1
        
        self.gen_quads_body(ir.body)

        self.add_quad(op=Operations.GOTO, vdir1=quad_pos_bef_eval)
        self.quads[open_pos].vdir2 = len(self.quads)

    def gen_quads_body(self, ir: Body): 
        for statement in ir.statements:
            self.generate_quads(statement)

    def gen_quads_f_call(self, ir: FCall): 
        self.current_scope = ir.id

        function_register = self.function_table.get_function(ir.id)
        if function_register is None:
            raise ValueError(f"Function {ir.id} is not declared.")

        if len(ir.args) != len(function_register.param_types):
            raise ValueError(f"Function {ir.id} expects {len(function_register.param_types)} arguments, got {len(ir.args)}.")

        self.add_quad(op=Operations.ALLOC, label=ir.id)
        
        for i, arg in enumerate(ir.args):
            expr_vdir = self.evaluate_expression(arg)
            expr_type = self.memory_manager.get_address_type(expr_vdir)

            param_type = function_register.param_types[i]
            if not self.semantic_cube.is_decl_valid(from_type=expr_type, to_type=param_type):
                raise ValueError(f"Invalid argument type: {expr_type} cannot be passed to function {ir.id}.")
            
            new_type = self.semantic_cube.get_resulting_type(
                type1=param_type, 
                type2=expr_type,
                operation=Operations.ASSIGN
            )

            print(f"Converting {expr_type} to {new_type}")
            if expr_type != new_type:
                # Convert the expression to the expected type
                prev_vdir = expr_vdir
                if new_type == "int":
                    expr_vdir = self.memory_manager.allocate(AllocCategory.TEMP_INT)
                elif new_type == "float":
                    expr_vdir = self.memory_manager.allocate(AllocCategory.TEMP_FLOAT)
                self.add_quad(op=Operations.ASSIGN, vdir1=prev_vdir, storage_vdir=expr_vdir)

            self.add_quad(op=Operations.PARAM, vdir1=expr_vdir)
        # Check if function is declared
        
            
        self.current_scope = "global"
