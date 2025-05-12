from dataclasses import dataclass
from turtle import left
from typing import cast, List, Union, Tuple, Optional
from SemanticCube import SemanticCube
from node_dataclasses import Expression, Exp, Term, Factor, Program, Quad
from SymbolTable import SymbolTable
# from lark import Tree

@dataclass
class EvaluatingExpression:
    value: Union[int, float]
    buffer_name: str

class BabyInterpreter:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.current_scope = "global"
        self.semantic_cube = SemanticCube()
        self.quads: List[Quad] = []
        self.buffer_index = 0

    def add_quad(
            self, 
            op: str, 
            buff1: Union[str, int, float], 
            buff2: Optional[Union[str, int, float]] = None, 
            storage_buff: Optional[str] = "t"
            ) -> Quad:
        """Add a quadruple to the list of quads."""

        if (storage_buff == "t"):
            storage_buff = f"t{self.buffer_index}"
            self.buffer_index += 1
        quad = Quad(op=op, buff1=buff1, buff2=buff2, storage_buff=storage_buff)
        self.quads.append(quad)
        return quad

    def evaluate_expression(self, current_tree_node) -> EvaluatingExpression :
        expr_class = current_tree_node.__class__.__name__
        if expr_class == "Expression":
            
            current_tree_node = cast(Expression, current_tree_node)
            left_exp = self.evaluate_expression(current_tree_node.left_expr)
            left_value = left_exp.value
            if current_tree_node.op is None or current_tree_node.right_expr is None:
                return left_exp
            
            right_exp = self.evaluate_expression(current_tree_node.right_expr)
            right_value = right_exp.value
            op = current_tree_node.op

            if op == '>':
                if left_value <= right_value:
                    quad = self.add_quad(op='>', buff1=left_exp.buffer_name, buff2=right_exp.buffer_name)
                    assert quad.storage_buff is not None
                    return EvaluatingExpression(1, quad.storage_buff)
            elif op == '<':
                quad = self.add_quad(op='>', buff1=left_exp.buffer_name, buff2=right_exp.buffer_name)
                assert quad.storage_buff is not None
                return EvaluatingExpression(1, quad.storage_buff)
            elif op == '!=':
                if left_value != right_value:
                    quad = self.add_quad(op='!=', buff1=left_exp.buffer_name, buff2=right_exp.buffer_name)
                    assert quad.storage_buff is not None
                    return EvaluatingExpression(1, quad.storage_buff)
            
            quad = self.add_quad(op=op, buff1=left_exp.buffer_name, buff2=right_exp.buffer_name)
            assert quad.storage_buff is not None
            return EvaluatingExpression(0, quad.storage_buff)
            
        
        elif expr_class == "Exp":
            current_tree_node = cast(Exp, current_tree_node)
            left_exp = self.evaluate_expression(current_tree_node.left_term)
            for op, term in current_tree_node.operations:
                right_exp = self.evaluate_expression(term)
                quad = self.add_quad(op=op, buff1=left_exp.buffer_name, buff2=right_exp.buffer_name)
                assert quad.storage_buff is not None
                result_value = self.semantic_cube.perform_operation(left_exp.value, right_exp.value, op)
                left_exp = EvaluatingExpression(result_value, quad.storage_buff)
            return left_exp
        
        elif expr_class == "Term":
            current_tree_node = cast(Term, current_tree_node)
            left_exp = self.evaluate_expression(current_tree_node.left_factor)
            for op, factor in current_tree_node.operations:
                right_exp = self.evaluate_expression(factor)
                quad = self.add_quad(op=op, buff1=left_exp.buffer_name, buff2=right_exp.buffer_name)
                assert quad.storage_buff is not None
                result_value = self.semantic_cube.perform_operation(left_exp.value, right_exp.value, op)
                left_exp = EvaluatingExpression(result_value, quad.storage_buff)
            return left_exp
        
        elif expr_class == "Factor":
            current_tree_node = cast(Factor, current_tree_node)
            if isinstance(current_tree_node.value, str):
                # Check if the value is a variable
                if self.symbol_table.is_symbol_declared(current_tree_node.value, self.current_scope):
                    value = self.symbol_table.get_symbol(current_tree_node.value, self.current_scope).value
                    if value is None:
                        raise ValueError(f"Variable {current_tree_node.value} is not initialized.")
                    return EvaluatingExpression(value, current_tree_node.value) # Stored in the symbol table
                else:
                    raise ValueError(f"Variable {current_tree_node.value} is not declared.")
                
            elif isinstance(current_tree_node.value, (int, float)):
                if current_tree_node.sign == '-':
                    ans = EvaluatingExpression(current_tree_node.value * -1, str(current_tree_node.value))
                    return ans
                else:
                    ans = EvaluatingExpression(current_tree_node.value, str(current_tree_node.value))
                    return ans
                
            elif isinstance(current_tree_node.value, Expression):
                return self.evaluate_expression(current_tree_node.value)
            
            else:
                raise ValueError(f"Unsupported factor type: {type(current_tree_node.value)}")
        
        else :
            raise ValueError(f"Unsupported expression type: {expr_class}")
    
    
    def execute(self, ir):
        ir_class = ir.__class__.__name__
        
        if ir_class == "Program": 
            self.execute_program(ir)

        elif ir_class == "Vars":
            self.execute_vars(ir)

        elif ir_class == "VarDeclaration":
            self.execute_var_declaration(ir)

        elif ir_class == "Function":
            self.execute_function(ir)

        elif ir_class == "Assign":
            self.execute_assign(ir)

        elif ir_class == "Print":
            self.execute_print(ir)

        elif ir_class == "Condition":
            self.execute_condition(ir)

        elif ir_class == "Cycle":
            self.execute_cycle(ir)

        elif ir_class == "Body":
            self.execute_body(ir)

        elif ir_class == "FCall":
            self.execute_f_call(ir)

        elif ir_class == "Expression":
            self.execute_expression(ir)

        elif ir_class == "Exp":
            self.execute_exp(ir)

        elif ir_class == "Term":
            self.execute_term(ir)

        elif ir_class == "Factor":
            self.execute_factor(ir)

    
    def execute_program(self, ir: Program):
        if ir.vars is not None: 
            self.execute_vars(ir.vars)
        for func in ir.funcs:
            self.execute_function(func)
        self.execute_body(ir.body)

    def execute_vars(self, ir): 
        for var_decl in ir.declarations:
            self.execute_var_declaration(var_decl)

    def execute_var_declaration(self, ir): 
        for var_name in ir.names:
            self.symbol_table.add_variable(name=var_name, data_type=ir.type_, scope_name=self.current_scope)
            self.add_quad(op='=', buff1=0, storage_buff=var_name)

    def execute_function(self, ir): 
        self.current_scope = ir.id
        self.symbol_table.add_function(name=ir.id, params=ir.params, body=ir.body, vars=ir.vars)
        # self.execute_body(ir.body)
        self.current_scope = "global"

    def execute_assign(self, ir): 
        # 1. Evaluate expression to get the value
        expr = self.evaluate_expression(ir.expr)
        # 2. Check if variable is declared
        if not self.symbol_table.is_symbol_declared(ir.id, self.current_scope):
            raise ValueError(f"Variable {ir.id} is not declared.")
        # 3. Check if types are compatible
        var_type = self.symbol_table.get_variable_type(ir.id, self.current_scope)
        is_valid_decl = self.semantic_cube.is_decl_valid(from_type=type(expr.value).__name__, to_type=var_type)
        if not is_valid_decl:
            raise ValueError(f"Invalid assignment: {type(expr.value).__name__} cannot be assigned to {var_type}.")
        
        # 4. Update the variable in the symbol table
        resulting_value = self.semantic_cube.convert_type(from_type=type(expr.value).__name__, to_type=var_type, value=expr.value)
        self.symbol_table.update_symbol_value(name=ir.id, value=resulting_value, scope_name=self.current_scope)

        # 5. Add quad for assignment
        quad = self.add_quad(op='=', buff1=ir.id, buff2=expr.buffer_name, storage_buff=None)

    def execute_print(self, ir): 
        for content in ir.contents:
            if isinstance(content, str):
                print(content, end=" ")
                self.add_quad(op='print', buff1=content, storage_buff=None)
            else:
                # Evaluate the expression and print its value
                expr = self.evaluate_expression(content)
                print(expr.value, end=" ")
                self.add_quad(op='print', buff1=expr.buffer_name, storage_buff=None)
        print()  # New line after printing all contents

    def execute_condition(self, ir): 
        if self.evaluate_expression(ir.condition):
            self.execute_body(ir.if_body)
        else:
            self.execute_body(ir.else_body)

    def execute_cycle(self, ir): 
        while self.evaluate_expression(ir.expr):
            self.execute_body(ir.body)

    def execute_body(self, ir): 
        for statement in ir.statements:
            self.execute(statement)

    def execute_f_call(self, ir): 
        self.current_scope = ir.id
        # Check if function is declared
        if not self.symbol_table.is_function_declared(ir.id):
            raise ValueError(f"Function {ir.id} is not declared.")
        
        # Evaluate expression for each parameter
        arg_values = []
        for i, arg in enumerate(ir.args):
            symbol = self.symbol_table.get_parameter(param_index=i, function_name=ir.id)
            # Evaluate the expression to get the value
            arg = self.evaluate_expression(arg)
            # Check if types are compatible
            is_valid_decl = self.semantic_cube.is_decl_valid(from_type=type(arg.value).__name__, to_type=symbol.data_type)
            if not is_valid_decl:
                raise ValueError(f"Invalid assignment: {type(arg).__name__} cannot be assigned to {symbol.data_type}.")
            
            # Store the parameter value
            arg_values.append(self.semantic_cube.convert_type(from_type=type(arg.value).__name__, to_type=symbol.data_type, value=arg.value))
        
        # Change parameter values in the symbol table
        for i, value in enumerate(arg_values):
            self.symbol_table.update_parameter_value(i, value, self.current_scope)
        # Execute the function body
        function_scope = self.symbol_table.get_scope(self.current_scope)
        self.execute_body(function_scope.body)
        
        # Clean parameter values after execution
        self.symbol_table.clean_params(function_name=self.current_scope)
        
        self.current_scope = "global"




    def execute_expression(self, ir): 
        pass

    def execute_exp(self, ir): 
        pass

    def execute_term(self, ir): 
        pass

    def execute_factor(self, ir): 
        pass
