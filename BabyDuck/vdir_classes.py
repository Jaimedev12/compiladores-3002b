from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Set, Union

class VariableType(Enum):
    GLOBAL_INT = 1
    GLOBAL_FLOAT = 2
    LOCAL_INT = 3
    LOCAL_FLOAT = 4
    TEMP_INT = 5
    TEMP_FLOAT = 6
    CONSTANT = 7

class Operations(Enum):
    PLUS = 1
    MINUS = 2
    MULT = 3
    DIV = 4
    LESS_THAN = 5
    GREATER_THAN = 6
    NOT_EQUAL = 7
    ASSIGN = 8
    PRINT = 9

@dataclass
class AddressRange:
    start: int
    end: int
    current: int

class MemoryManager:
    def __init__(self):
        self.address_ranges = {
            VariableType.GLOBAL_INT: AddressRange(1000, 1999, 1000),
            VariableType.GLOBAL_FLOAT: AddressRange(2000, 2999, current=2000),
            VariableType.LOCAL_INT: AddressRange(3000, 3999, current=3000),
            VariableType.LOCAL_FLOAT: AddressRange(4000, 4999, current=4000),
            VariableType.TEMP_INT: AddressRange(5000, 5999, 5000),
            VariableType.TEMP_FLOAT: AddressRange(6000, 6999, 6000),
            VariableType.CONSTANT: AddressRange(7000, 7999, 7000),
        }

        self.current_per_local: Dict[str, int] = dict()

        self.constants_string: Dict[str, int] = dict()
        self.constants_int: Dict[int, int] = dict()
        self.constants_float: Dict[float, int] = dict()

    def _allocate_local(self, local_name: Optional[str], var_type: VariableType) -> int:
        if local_name is None:
            raise ValueError("Local name must be provided for local variables.")
        if local_name not in self.current_per_local:
            self.current_per_local[local_name] = 0

        range_info = self.address_ranges[var_type]
        if self.current_per_local[local_name] > range_info.end - range_info.start:
            raise OverflowError(f"No more memory in {var_type.name} range for {local_name}")

        address = range_info.start + self.current_per_local[local_name]
        self.current_per_local[local_name] += 1
        return address

    def _allocate_constant(self, value: Optional[Union[int, float, str]]) -> int:
        if value is None:
            raise ValueError("Constant value must be provided for constant variables.")
        address = self.address_ranges[VariableType.CONSTANT].current
        
        if isinstance(value, str):
            if value in self.constants_string.keys():
                return self.constants_string[value]
            else:
                self.constants_string[value] = address
    
        if isinstance(value, int):
            if value in self.constants_int.keys():
                return self.constants_int[value]
            else:
                self.constants_int[value] = address
            
        if isinstance(value, float):
            if value in self.constants_float.keys():
                return self.constants_float[value]
            else:
                self.constants_float[value] = address

        self.address_ranges[VariableType.CONSTANT].current += 1
        return address


    def allocate(
            self, 
            var_type: VariableType, 
            local_name: Optional[str] = None, 
            const_value: Optional[Union[int, float, str]] = None
            ) -> int:
        if var_type == VariableType.LOCAL_INT or var_type == VariableType.LOCAL_FLOAT:
            return self._allocate_local(local_name, var_type)

        if var_type == VariableType.CONSTANT:
            return self._allocate_constant(const_value)
        if var_type not in self.address_ranges:
            raise ValueError(f"Invalid variable type: {var_type}")

        range_info = self.address_ranges[var_type]
        if range_info.current > range_info.end:
            raise OverflowError(f"No more memory in {var_type.name} range")

        address = range_info.current
        range_info.current += 1
        return address