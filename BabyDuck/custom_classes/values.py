from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union, Tuple, Literal

ValueType = Literal["int", "float", "str"]
ConstantValue = Union[int, float, str]

VariableType = Literal["int", "float"]
VariableValues = Union[int, float]