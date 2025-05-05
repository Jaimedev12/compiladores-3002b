from dataclasses import dataclass, field
from typing import List, Optional, Union, Tuple

@dataclass
class Expression():
    left_expr: 'Exp'
    operations: List[Tuple[str, 'Exp']] = field(default_factory=list) # List of tuples (operator, expression)

@dataclass
class Exp():
    left_term: 'Term'
    operations : List[Tuple[str, 'Term']] = field(default_factory=list)  # List of tuples (operator, term)

@dataclass
class Term():
    left_factor: 'Factor'
    operations: List[Tuple[str, 'Factor']] = field(default_factory=list)  # List of tuples (operator, factor)

@dataclass
class Factor():
    value: Union[int, float, str, Expression] = 0
    sign: Optional[str] = None  # '+' or '-'


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
    type_: str
    names: List[str]

# Functions
@dataclass
class Function():
    return_type: str
    id: str
    params: List['Param']
    vars: Optional['Vars']
    body: 'Body'

@dataclass
class Param():
    name: str
    type_: str

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


@dataclass
class Comparison():
    left: Expression
    operator: str
    right: Expression

@dataclass
class ExpressionCompound():
    comparisons: List[Comparison]