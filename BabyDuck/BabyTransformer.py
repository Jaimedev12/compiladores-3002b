from lark import Transformer, v_args
from lark import Lark
from node_dataclasses import Program, Vars, VarDeclaration, Function, Param, Assign, Print, Condition, Cycle, Body, FCall, Expression, Exp, Term, Factor, Statement
from typing import cast, List, Any
from MemoryManager import Operations

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
        return Program(id=args[1], vars=None, funcs=[], body=args[-2])  
    
    def program_no_vars(self, *args):
        funcs = cast(List[Function], args[3:-3])
        return Program(id=args[1], vars=None, funcs=funcs, body=args[-2])
    
    def program_no_funcs(self, *args):
        return Program(id=args[1], vars=args[3], funcs=[], body=args[-2])
    
    def program_all(self, *args):
        funcs = cast(List[Function], args[4:-3])
        return Program(id=args[1], vars=args[3], funcs=funcs, body=args[-2])

    """
    ?statement: assign -> statement_assign
            | condition -> statement_condition
            | cycle -> statement_cycle
            | f_call -> statement_f_call
            | print -> statement_print
    """
    def statement_assign(self, assign_node):
        return assign_node
    
    def statement_condition(self, condition_node):
        return condition_node
    
    def statement_cycle(self, cycle_node):
        return cycle_node
    
    def statement_f_call(self, f_call_node):
        return f_call_node
    
    def statement_print(self, print_node):
        return print_node

    """
    assign: ID EQUAL expression SEMICOLON
    """
    def assign(self, *args):
        return Assign(id=args[0], expr=args[2])

    """
    vars: VAR (var_declaration)+
    ?var_declaration: ID COLON type_ SEMICOLON -> var_declaration_single
        | ID (COMMA ID)+ COLON type_ SEMICOLON -> var_declaration_multiple
    """
    def vars(self, var_token, *declarations):
        decls = cast(List[VarDeclaration], declarations)
        return Vars(declarations=decls)
    
    def var_declaration_single(self, *args):
        return VarDeclaration(type_ = args[-2], names=[args[0]])
    
    def var_declaration_multiple(self, *args):
        var_list = [args[0]]
        for i in range(2, len(args)-3, 2):
            id = args[i]
            var_list.append(id)
        return VarDeclaration(type_ = args[-2], names=var_list)


    """
    ?funcs: (VOID | type_) ID OPEN_PAREN CLOSE_PAREN OPEN_BRACKET body CLOSE_BRACKET SEMICOLON -> funcs_no_params_no_vars
            | (VOID | type_) ID OPEN_PAREN CLOSE_PAREN OPEN_BRACKET vars body CLOSE_BRACKET SEMICOLON -> funcs_no_params
            | (VOID | type_) ID OPEN_PAREN params CLOSE_PAREN OPEN_BRACKET body CLOSE_BRACKET SEMICOLON -> funcs_no_vars
            | (VOID | type_) ID OPEN_PAREN params CLOSE_PAREN OPEN_BRACKET vars body CLOSE_BRACKET SEMICOLON -> funcs_all
    """
    def funcs_no_params_no_vars(self, *args):
        return Function(return_type=args[0], id=args[1], params=[], vars=None, body=args[-3])
    
    def funcs_no_params(self, *args):
        return Function(return_type=args[0], id=args[1], params=[], vars=args[-4], body=args[-3])
    
    def funcs_no_vars(self, *args):
        return Function(return_type=args[0], id=args[1], params=args[3], vars=None, body=args[6])
    
    def funcs_all(self, *args):
        return Function(return_type=args[0], id=args[1], params=args[3], vars=args[6], body=args[7])


    """
    ?params: ID COLON type_ -> params_single
            | ID COLON type_ (COMMA ID COLON type_)+ -> params_multiple
    """
    def params_single(self, id, _, type_):
        return [Param(name=id, type_=type_)]
    
    def params_multiple(self, first_id, _, first_type, *rest):
        params = [Param(name=first_id, type_=first_type)]
        for i in range(0, len(rest), 4):
            id = rest[i+1]
            type_ = rest[i+3]
            params.append(Param(name=id, type_=type_))
        return params
    

    """
    f_call: ID OPEN_PAREN CLOSE_PAREN SEMICOLON -> f_call_no_args
        | ID OPEN_PAREN arguments CLOSE_PAREN SEMICOLON -> f_call_with_args
    ?arguments: expression -> arguments_single
            | expression (COMMA expression)+ -> arguments_multiple
    """
    def f_call_no_args(self, id):
        return FCall(id=id, args=[])
    
    def f_call_with_args(self, id, *rest):
        args = cast(List[Expression], rest[1])
        return FCall(id=id, args=args)
    
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
        return Print(contents=[args[2]])
    
    def print_multiple(self, *args):
        print_contents = [args[2]]
        for i in range(3, len(args)-2, 2):
            print_contents.append(args[i+1])
            
        return Print(contents=print_contents)
    
    def print_expression(self, expr):
        return expr
    
    def print_string(self, string):
        return string[1:-1]

    """
    ?condition: IF OPEN_PAREN expression CLOSE_PAREN body SEMICOLON -> condition_if
            | IF OPEN_PAREN expression CLOSE_PAREN body (ELSE body) SEMICOLON -> condition_else
    """
    def condition_if(self, *args):
        return Condition(expr=args[2], if_body=args[-2], else_body=None)
    
    def condition_else(self, *args):
        return Condition(expr=args[2], if_body=args[-4], else_body=args[-2])

    """
    cycle: WHILE OPEN_PAREN expression CLOSE_PAREN DO body SEMICOLON
    """
    def cycle(self, *args):
        return Cycle(expr=args[2], body=args[-2])

    """
    ?body: OPEN_KEY CLOSE_KEY -> body_empty
            | OPEN_KEY statement+ CLOSE_KEY -> body_block
    """
    def body_empty(self, *args):
        return Body(statements=[])
    
    def body_block(self, *statements):
        statements = cast(List[Statement], statements[1:-1])
        return Body(statements=statements)
    

    """
    ?expression: exp -> expression_simple
        | exp comparison_op exp -> expression_compound
    """
    def expression_simple(self, exp):
        return Expression(left_expr=exp)
    
    def expression_compound(self, exp1, op, exp2):
        return Expression(left_expr=exp1, op=op, right_expr=exp2)

    """
    ?exp: term -> exp_simple
        | term ((SUB | ADD) term)+ -> exp_compound
    """
    def exp_simple(self, term):
        return Exp(left_term=term, operations=[])
    
    def exp_compound(self, *terms):
        opers = []
        for i in range(1, len(terms), 2):
            op_token = terms[i]
            op = Operations.PLUS
            if op_token == '-':
                op = Operations.MINUS
            term = terms[i+1]
            opers.append((op, term))
        return Exp(left_term=terms[0], operations=opers)

    """
    ?term: factor -> term_simple
        | factor ((MULT | DIV) factor)+ -> term_compound
    """
    def term_simple(self, factor):
        return Term(left_factor=factor, operations=[])
    
    def term_compound(self, *factors):
        opers = []
        for i in range(1, len(factors), 2):
            op_token = factors[i]
            op = Operations.MULT
            if op_token == '/':
                op = Operations.DIV
            term = factors[i+1]
            opers.append((op, term))
        return Term(left_factor=factors[0], operations=opers)
    
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
        return Factor(value=args[1])
    
    def factor_cte(self, cte):
        return Factor(value=cte, sign='+')

    def factor_id(self, id):
        return Factor(value=id, sign='+')

    def factor_cte_add(self, add, cte):
        return Factor(value=cte, sign='+')

    def factor_id_add(self, add, id):
        return Factor(value=id, sign='+')

    def factor_cte_sub(self, sub, cte):
        return Factor(value=cte, sign='-')

    def factor_id_sub(self, sub, id):
        return Factor(value=id, sign='-')

    
    """
    ?type_: "int" -> type_int
            | "float" -> type_float
    comparison_op: GREATER | LESS | DIFFERENT
    cte: INT -> int
            | FLOAT -> float
    ID: CNAME
    """
    def type_int(self):
        return "int"
    
    def type_float(self):
        return "float"
    
    def int(self, value):
        return int(value)
    
    def float(self, value):
        return float(value)
    
    def ID(self, id):
        return str(id)
    
    def comparison_op(self, op):
        return str(op)
    
    
# Load the grammar and create the parser
def get_parser():
    with open("grammar.lark", "r") as f:
        grammar = f.read()
    return Lark(grammar, parser="lalr", transformer=BabyTransformer())