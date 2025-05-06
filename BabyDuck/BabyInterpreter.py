from SemanticCube import SemanticCube
from node_dataclasses import Expression
# from lark import Tree

class BabyInterpreter:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.current_scope = "global"
        self.semantic_cube = SemanticCube()

    def evaluate_expression(self, expr_tree):
        expr_class = expr_tree.__class__.__name__
        if expr_class == "Expression":
            
            last_value = self.evaluate_expression(expr_tree.left_expr)
            if len(expr_tree.operations) == 0:
                return last_value
            
            flag = False
            for op, expr in expr_tree.operations:
                right_value = self.evaluate_expression(expr)
    
                if op == '>':
                    if last_value <= right_value:
                        flag = True
                elif op == '<':
                    if last_value >= right_value:
                        flag = True
                elif op == '!=':
                    if last_value == right_value:
                        flag = True
                else:
                    raise ValueError(f"Unsupported operator: {op}")
                
                last_value = right_value
                    
            if flag:
                return 0
            else:
                return 1
        
        elif expr_class == "Exp":
            left_value = self.evaluate_expression(expr_tree.left_term)
            for op, term in expr_tree.operations:
                right_value = self.evaluate_expression(term)
                left_value = self.semantic_cube.get_resulting_type(left_value, right_value, op)
            return left_value
        
        elif expr_class == "Term":
            left_value = self.evaluate_expression(expr_tree.left_factor)
            for op, factor in expr_tree.operations:
                right_value = self.evaluate_expression(factor)
                left_value = self.semantic_cube.get_resulting_type(left_value, right_value, op)
            return left_value
        
        elif expr_class == "Factor":
            if isinstance(expr_tree.value, str):
                # Check if the value is a variable
                if self.symbol_table.is_symbol_declared(expr_tree.value, self.current_scope):
                    return self.symbol_table.get_symbol_value(expr_tree.value, self.current_scope)
                else:
                    raise ValueError(f"Variable {expr_tree.value} is not declared.")
                
            elif isinstance(expr_tree.value, (int, float)):
                if expr_tree.sign == '-':
                    return -expr_tree.value
                else:
                    return expr_tree.value
                
            elif isinstance(expr_tree.value, Expression):
                return self.evaluate_expression(expr_tree.value)
            
            else:
                raise ValueError(f"Unsupported factor type: {type(expr_tree.value)}")
    
    
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

    
    def execute_program(self, ir):
        if vars is not None: 
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

    def execute_function(self, ir): 
        self.current_scope = ir.id
        self.symbol_table.add_function(name=ir.id, params=ir.params, body=ir.body)
        self.execute_body(ir.body)
        self.current_scope = "global"

    def execute_assign(self, ir): 
        # 1. Evaluate expression to get the value
        expr_value = self.evaluate_expression(ir.expr)
        # 2. Check if variable is declared
        if not self.symbol_table.is_symbol_declared(ir.id, self.current_scope):
            raise ValueError(f"Variable {ir.id} is not declared.")
        # 3. Check if types are compatible
        var_type = self.symbol_table.get_variable_type(ir.id, self.current_scope)
        is_valid_decl = self.semantic_cube.is_decl_valid(from_type=type(expr_value).__name__, to_type=var_type)
        if not is_valid_decl:
            raise ValueError(f"Invalid assignment: {type(expr_value).__name__} cannot be assigned to {var_type}.")
        
        # 4. Update the variable in the symbol table
        resulting_value = self.semantic_cube.convert_type(from_type=type(expr_value).__name__, to_type=var_type, value=expr_value)
        self.symbol_table.update_symbol_value(name=ir.id, value=resulting_value, scope_name=self.current_scope)

    def execute_print(self, ir): 
        for content in ir.contents:
            if isinstance(content, str):
                print(content, end=" ")
            else:
                # Evaluate the expression and print its value
                expr_value = self.evaluate_expression(content)
                print(expr_value, end=" ")

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
            arg_value = self.evaluate_expression(arg)
            # Check if types are compatible
            is_valid_decl = self.semantic_cube.is_decl_valid(from_type=type(arg_value).__name__, to_type=symbol.data_type)
            if not is_valid_decl:
                raise ValueError(f"Invalid assignment: {type(arg_value).__name__} cannot be assigned to {symbol.data_type}.")
            
            # Store the parameter value
            arg_values.append(self.semantic_cube.convert_type(from_type=type(arg_value).__name__, to_type=symbol.data_type, value=arg_value))
        
        # Change parameter values in the symbol table
        for i, value in enumerate(arg_values):
            self.symbol_table.update_parameter_value(param_index=i, value=value, scope_name=self.current_scope)
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
