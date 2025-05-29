# from dataclasses import dataclass, field
# from enum import Enum
# from typing import List, Optional, Union, Tuple, Literal

# ValueType = Literal["int", "float", "str"]
# ConstantValue = Union[int, float, str]

# VariableType = Literal["int", "float"]
# VariableValues = Union[int, float]


# class AllocCategory(Enum):
#     GLOBAL_INT = 1
#     GLOBAL_FLOAT = 2
#     LOCAL_INT = 3
#     LOCAL_FLOAT = 4
#     TEMP_INT = 5
#     TEMP_FLOAT = 6
#     CONSTANT = 7

# class Operations(Enum):
#     PLUS = 1
#     MINUS = 2
#     MULT = 3
#     DIV = 4
#     LESS_THAN = 5
#     GREATER_THAN = 6
#     NOT_EQUAL = 7
#     ASSIGN = 8
#     PRINT = 9
#     GOTOF = 10
#     GOTO = 11
#     END = 12
#     ALLOC = 13
#     PARAM = 14
#     CALL = 15
#     ENDFUNC = 16
#     GOSUB = 17

# @dataclass
# class AddressRange:
#     start: int
#     end: int
#     current: int


# @dataclass
# class Symbol:
#     name: str
#     data_type: VariableType
#     vdir: int = 0
#     value: Optional[Union[int, float]] = None
#     is_param: bool = False
#     param_index: Optional[int] = None


# @dataclass
# class Quad():
#     op_vdir: int
#     vdir1: Optional[int] = None
#     vdir2: Optional[int] = None
#     storage_vdir: Optional[int] = None
#     label: Optional[str] = None
#     scope: str = "global"

# @dataclass
# class Expression():
#     left_expr: 'Exp'
#     op : Optional[Union[Literal[Operations.GREATER_THAN], Literal[Operations.LESS_THAN], Literal[Operations.NOT_EQUAL]]] = None
#     right_expr: Optional['Exp'] = None  # Right-hand side expression (if any)

# @dataclass
# class Exp():
#     left_term: 'Term'
#     operations : List[ \
#         Tuple[Union[Literal[Operations.PLUS], Literal[Operations.MINUS]], 'Term'] \
#         ] = field(default_factory=list)  # List of tuples (operator, term)

# @dataclass
# class Term():
#     left_factor: 'Factor'
#     operations: List[ \
#         Tuple[Union[Literal[Operations.MULT], Literal[Operations.DIV]], 'Factor'] \
#         ] = field(default_factory=list)  # List of tuples (operator, factor)

# @dataclass
# class Factor():
#     value: Union[int, float, str, Expression] = 0
#     sign: Optional[Union[Literal["+"], Literal["-"]]] = None


# @dataclass
# class Statement():
#     pass

# # Program
# @dataclass
# class Program():
#     id: str
#     vars: Optional['Vars']
#     funcs: List['Function']
#     body: 'Body'

# # Variables
# @dataclass
# class Vars():
#     declarations: List['VarDeclaration']

# @dataclass
# class VarDeclaration():
#     type_: VariableType
#     names: List[str]

# # Functions
# @dataclass
# class Function():
#     id: str
#     params: List['Param']
#     vars: Optional['Vars']
#     body: 'Body'

# @dataclass
# class Param():
#     name: str
#     type_: VariableType

# # Statements
# @dataclass
# class Assign(Statement):
#     id: str
#     expr: Expression

# @dataclass
# class Print(Statement):
#     contents: List[Union[Expression, str]]

# @dataclass
# class Condition(Statement):
#     expr: Expression
#     if_body: 'Body'
#     else_body: Optional['Body'] = None

# @dataclass
# class Cycle(Statement):
#     expr: Expression
#     body: 'Body'

# @dataclass
# class Body():
#     statements: List[Statement]

# @dataclass
# class FCall(Statement):
#     id: str
#     args: List[Expression]