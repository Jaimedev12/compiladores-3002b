from lark import Transformer, v_args
from lark import Lark

@v_args(inline=True)
class BabyTransformer(Transformer):
    def __init__(self):
        self.current_scope = None

    """
    ?program_: PROGRAM ID SEMICOLON MAIN body END -> program_no_vars_no_funcs
            | PROGRAM ID SEMICOLON funcs+ MAIN body END -> program_no_vars
            | PROGRAM ID SEMICOLON vars MAIN body END -> program_no_funcs
            | PROGRAM ID SEMICOLON vars funcs+ MAIN body END -> program_all
    """

    def program_no_vars_no_funcs(self, *args):
        id = args[1]
        body = args[-2]
        return ("program", id, None, [], body)
    
    def program_no_vars(self, *args):
        id = args[1]
        funcs = args[3:-3]
        body = args[-2]
        return ("program", id, None, list(funcs), body)
    
    def program_no_funcs(self, *args):
        id = args[1]
        vars = args[3]
        body = args[6]
        return ("program", id, vars, [], body)
    
    def program_all(self, *args):
        id = args[1]
        vars = args[3]
        funcs = args[4:-3]
        body = args[-2]
        return ("program", id, vars, list(funcs), body)

    """
    ?statement: assign -> statement_assign
            | condition -> statement_condition
            | cycle -> statement_cycle
            | f_call -> statement_f_call
            | print -> statement_print
    """
    def statement_assign(self, assign_node):
        return ("statement_assign", assign_node)
    
    def statement_condition(self, condition_node):
        return ("statement_condition", condition_node)
    
    def statement_cycle(self, cycle_node):
        return ("statement_cycle", cycle_node)
    
    def statement_f_call(self, f_call_node):
        return ("statement_f_call", f_call_node)
    
    def statement_print(self, print_node):
        return ("statement_print", print_node)

    """
    assign: ID EQUAL expression SEMICOLON
    """
    # def assign(self, id, expr):
    #     return ("assign", id, expr)
    def assign(self, *args):
        id = args[0]
        expr = args[2]
        return ("assign", id, expr)


    """
    vars: VAR (var_declaration)+
    ?var_declaration: ID COLON type_ SEMICOLON -> var_declaration_single
        | ID (COMMA ID)+ COLON type_ SEMICOLON -> var_declaration_multiple
    """
    def vars(self, var_token, *declarations):
        var_list = []
        for decl in declarations:
            for var_name in decl[2]:
                var_list.append((var_name, decl[1]))
        return ("vars", declarations)
    
    def var_declaration_single(self, *args):
        return ("var_declaration", args[-2], [args[0]])
    
    def var_declaration_multiple(self, *args):
        var_list = [args[0]]
        for i in range(2, len(args)-3, 2):
            id = args[i]
            var_list.append(id)
        return ("var_declaration", args[-2], var_list)


    """
    ?funcs: (VOID | type_) ID OPEN_PAREN CLOSE_PAREN OPEN_BRACKET body CLOSE_BRACKET SEMICOLON -> funcs_no_params_no_vars
            | (VOID | type_) ID OPEN_PAREN CLOSE_PAREN OPEN_BRACKET vars body CLOSE_BRACKET SEMICOLON -> funcs_no_params
            | (VOID | type_) ID OPEN_PAREN params CLOSE_PAREN OPEN_BRACKET body CLOSE_BRACKET SEMICOLON -> funcs_no_vars
            | (VOID | type_) ID OPEN_PAREN params CLOSE_PAREN OPEN_BRACKET vars body CLOSE_BRACKET SEMICOLON -> funcs_all
    """
    def funcs_no_params_no_vars(self, *args):
        return_type = args[0]
        id = args[1]
        body = args[-3]
        return ("function", return_type, id, [], None, body)
    
    def funcs_no_params(self, *args):
        return_type = args[0]
        id = args[1]
        vars = args[-4]
        body = args[-3]
        return ("function", return_type, id, [], vars, body)
    
    def funcs_no_vars(self, *args):
        return_type = args[0]
        id = args[1]
        params = args[3]
        body = args[6]
        return ("function", return_type, id, params, None, body)
    
    def funcs_all(self, *args):
        return_type = args[0]
        id = args[1]
        params = args[3]
        vars = args[6]
        body = args[7]
        return ("function", return_type, id, params, vars, body)


    """
    ?params: ID COLON type_ -> params_single
            | ID COLON type_ (COMMA ID COLON type_)+ -> params_multiple
    """
    def params_single(self, id, _, type_):
        return [(id, type_)]
    
    def params_multiple(self, first_id, _, first_type, *rest):
        params = [(first_id, first_type)]
        for i in range(0, len(rest), 4):
            id = rest[i+1]
            type_ = rest[i+3]
            params.append((id, type_))
        return params
    

    """
    f_call: ID OPEN_PAREN CLOSE_PAREN SEMICOLON -> f_call_no_args
        | ID OPEN_PAREN arguments CLOSE_PAREN SEMICOLON -> f_call_with_args
    ?arguments: expression -> arguments_single
            | expression (COMMA expression)+ -> arguments_multiple
    """
    def f_call_no_args(self, id):
        return ("f_call", id, [])
    
    def f_call_with_args(self, id, *rest):
        return ("f_call", id, list(rest[2:-2]))
    
    def arguments_simple(self, expr):
        return [expr]
    
    def arguments_multiple(self, first_expr, *rest):
        args = [first_expr]
        for i in range(0, len(rest), 2):
            args.append(rest[i+1])
        return args

    """
    ?print: PRINT OPEN_PAREN print_content CLOSE_PAREN SEMICOLON -> print_single
            | PRINT OPEN_PAREN print_content (COMMA print_content)+ CLOSE_PAREN SEMICOLON -> print_multiple
    ?print_content: expression -> print_expression
            | ESCAPED_STRING -> print_string
    """
    def print_single(self, *args):
        return ("print", [args[2]])
    
    def print_multiple(self, *args):
        print_contents = [args[2]]
        for i in range(3, len(args)-2, 2):
            print_contents.append(args[i+1])
            
        return ("print", print_contents)
    
    def print_expression(self, expr):
        return ("print_expression", expr)
    
    def print_string(self, string):
        return ("print_string", string[1:-1])

    """
    ?condition: IF OPEN_PAREN expression CLOSE_PAREN body SEMICOLON -> condition_if
            | IF OPEN_PAREN expression CLOSE_PAREN body (ELSE body) SEMICOLON -> condition_else
    """
    def condition_if(self, *args):
        expr = args[2]
        body = args[-2]
        return ("condition", expr, body, None)
    
    def condition_else(self, *args):
        expr = args[2]
        if_body = args[-4]
        else_body = args[-2]
        return ("condition", expr, if_body, else_body)

    """
    cycle: WHILE OPEN_PAREN expression CLOSE_PAREN DO body SEMICOLON
    """
    def cycle(self, *args):
        expr = args[2]
        body = args[-2]
        return ("cycle", expr, body)

    """
    ?body: OPEN_KEY CLOSE_KEY -> body_empty
            | OPEN_KEY statement+ CLOSE_KEY -> body_block
    """
    def body_empty(self):
        return ("body", [])
    
    def body_block(self, *statements):
        return ("body", list(statements[1:-1]))
    

    """
    ?expression: exp -> expression_simple
            | exp (comparison_op exp)+ -> expression_compound
    """
    def expression_simple(self, exp):
        return ("expression_simple", exp)
    
    def expression_compound(self, *conditions):
        return ("expression_compound", list(conditions))

    """
    ?exp: term -> exp_simple
            | term (SUB term)+ -> exp_sub
            | term (ADD term)+ -> exp_add
    """
    def exp_simple(self, term):
        return ("exp_simple", term)
    
    def exp_sub(self, *terms):
        result = terms[0]
        for i in range(1, len(terms), 2):
            term = terms[i+1]
            result.append(term)
        return ("exp_sub", result)
    
    def exp_add(self, *terms):
        result = terms[0]
        for i in range(1, len(terms), 2):
            term = terms[i+1]
            result.append(term)
        return ("exp_add", result)

    """
    ?term: factor -> term_simple
            | factor (MULT factor)+ -> term_mult
            | factor (DIV factor)+ -> term_div     
    """
    def term_simple(self, factor):
        return ("term_simple", factor)
    
    def term_mult(self, *factors):
        result = factors[0]
        for i in range(1, len(factors), 2):
            term = factors[i+1]
            result.append(term)
        return ("term_mult", result)
    
    def term_div(self, *factors):
        result = factors[0]
        for i in range(1, len(factors), 2):
            term = factors[i+1]
            result.append(term)
        return ("term_div", result)
    
    
    """
    ?factor: OPEN_PAREN expression CLOSE_PAREN -> factor_expression
            | cte -> factor_cte
            | ID -> factor_id
            | ADD cte -> factor_cte_add
            | ADD ID -> factor_id_add
            | SUB cte -> factor_cte_sub
            | SUB ID -> factor_id_sub
    """
    def factor_expression(self, *args):
        return ("factor_expression", args[1])
    
    def factor_cte(self, cte):
        return ("factor_cte", cte)

    def factor_id(self, id):
        return ("factor_id", id)

    def factor_cte_add(self, add, cte):
        return ("factor_cte_add", cte)

    def factor_id_add(self, add, id):
        return ("factor_id_add", id)

    def factor_cte_sub(self, sub, cte):
        return ("factor_cte_sub", cte)

    def factor_id_sub(self, sub, id):
        return ("factor_id_sub", id)

    
    """
    ?type_: "int" -> type_int
            | "float" -> type_float
    comparison_op: GREATER | LESS | DIFFERENT
    cte: INT -> int
            | FLOAT -> float
    ID: CNAME
    """
    def type_int(self):
        # return ("type", "int")
        return "int"
    
    def type_float(self):
        # return ("type", "float")
        return "float"
    
    def int(self, value):
        return int(value)
    
    def float(self, value):
        return float(value)
    
    def ID(self, id):
        return str(id)
    
    
    
    
# Load the grammar and create the parser
def get_parser():
    with open("grammar.lark", "r") as f:
        grammar = f.read()
    return Lark(grammar, parser="lalr", transformer=BabyTransformer())