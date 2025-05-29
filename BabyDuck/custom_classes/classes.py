from dataclasses import dataclass
from typing import Optional, Union
from custom_classes.values import VariableType

@dataclass
class Symbol:
    name: str
    data_type: VariableType
    vdir: int = 0
    value: Optional[Union[int, float]] = None
    is_param: bool = False
    param_index: Optional[int] = None


@dataclass
class Quad():
    op_vdir: int
    vdir1: Optional[int] = None
    vdir2: Optional[int] = None
    storage_vdir: Optional[int] = None
    label: Optional[str] = None
    scope: str = "global"