from dataclasses import dataclass, field
from typing import List, Optional, Union, Tuple, Literal
from custom_classes.memory import Operations
from custom_classes.values import VariableType

@dataclass
class Expression():
    left_expr: 'Exp'
    op : Optional[Union[Literal[Operations.GREATER_THAN], Literal[Operations.LESS_THAN], Literal[Operations.NOT_EQUAL]]] = None
    right_expr: Optional['Exp'] = None  # Right-hand side expression (if any)

@dataclass
class Exp():
    left_term: 'Term'
    operations : List[ \
        Tuple[Union[Literal[Operations.PLUS], Literal[Operations.MINUS]], 'Term'] \
        ] = field(default_factory=list)  # List of tuples (operator, term)

@dataclass
class Term():
    left_factor: 'Factor'
    operations: List[ \
        Tuple[Union[Literal[Operations.MULT], Literal[Operations.DIV]], 'Factor'] \
        ] = field(default_factory=list)  # List of tuples (operator, factor)

@dataclass
class Factor():
    value: Union[int, float, str, Expression] = 0
    sign: Optional[Union[Literal["+"], Literal["-"]]] = None


@dataclass
class Statement():
    pass

# Program
@dataclass
class Program():
    id: str
    vars: Optional['Vars']
    funcs: List['Function']
    body: 'Body'

# Variables
@dataclass
class Vars():
    declarations: List['VarDeclaration']

@dataclass
class VarDeclaration():
    type_: VariableType
    names: List[str]

# Functions
@dataclass
class Function():
    id: str
    params: List['Param']
    vars: Optional['Vars']
    body: 'Body'

@dataclass
class Param():
    name: str
    type_: VariableType

# Statements
@dataclass
class Assign(Statement):
    id: str
    expr: Expression

@dataclass
class Print(Statement):
    contents: List[Union[Expression, str]]

@dataclass
class Condition(Statement):
    expr: Expression
    if_body: 'Body'
    else_body: Optional['Body'] = None

@dataclass
class Cycle(Statement):
    expr: Expression
    body: 'Body'

@dataclass
class Body():
    statements: List[Statement]

@dataclass
class FCall(Statement):
    id: str
    args: List[Expression]