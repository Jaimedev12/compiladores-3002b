from dataclasses import dataclass
from enum import Enum
from tkinter import END
from typing import Dict, Literal, Optional, Set, Union

class AllocCategory(Enum):
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
    GOTOF = 10
    GOTO = 11
    END = 12

@dataclass
class AddressRange:
    start: int
    end: int
    current: int

class MemoryManager:
    def __init__(self,
                global_int_start: int = 1000,
                global_float_start: int = 2000,
                local_int_start: int = 3000,
                local_float_start: int = 4000,
                temp_int_start: int = 5000,
                temp_float_start: int = 6000,
                constant_start: int = 7000,
                range_size: int = 1000
            ):
        self.address_ranges = {
            AllocCategory.GLOBAL_INT: AddressRange(global_int_start, global_int_start + range_size - 1, current=global_int_start),
            AllocCategory.GLOBAL_FLOAT: AddressRange(global_float_start, global_float_start + range_size - 1, current=global_float_start),
            AllocCategory.LOCAL_INT: AddressRange(local_int_start, local_int_start + range_size - 1, current=local_int_start),
            AllocCategory.LOCAL_FLOAT: AddressRange(local_float_start, local_float_start + range_size - 1, current=local_float_start),
            AllocCategory.TEMP_INT: AddressRange(temp_int_start, temp_int_start + range_size - 1, current=temp_int_start),
            AllocCategory.TEMP_FLOAT: AddressRange(temp_float_start, temp_float_start + range_size - 1, current=temp_float_start),
            AllocCategory.CONSTANT: AddressRange(constant_start, constant_start + range_size - 1, current=constant_start),
        }

        self.current_per_local: Dict[str, int] = dict()

        self.constants_string: Dict[str, int] = dict()
        self.constants_int: Dict[int, int] = dict()
        self.constants_float: Dict[float, int] = dict()
        self.constants: Dict[int, Union[int, float, str]] = dict()

    def _allocate_local(self, local_name: Optional[str], var_type: AllocCategory) -> int:
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
        address = self.address_ranges[AllocCategory.CONSTANT].current
        
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

        self.constants[address] = value
        self.address_ranges[AllocCategory.CONSTANT].current += 1
        return address


    def allocate(
            self, 
            var_type: AllocCategory, 
            local_name: Optional[str] = None, 
            const_value: Optional[Union[int, float, str]] = None
            ) -> int:
        if var_type == AllocCategory.LOCAL_INT or var_type == AllocCategory.LOCAL_FLOAT:
            return self._allocate_local(local_name, var_type)

        if var_type == AllocCategory.CONSTANT:
            return self._allocate_constant(const_value)
        if var_type not in self.address_ranges:
            raise ValueError(f"Invalid variable type: {var_type}")

        range_info = self.address_ranges[var_type]
        if range_info.current > range_info.end:
            raise OverflowError(f"No more memory in {var_type.name} range")

        address = range_info.current
        range_info.current += 1
        return address
    
    def get_address_type(self, address: int) -> Union[Literal["int"], Literal["float"], Literal["str"]]:

        if address < self.address_ranges[AllocCategory.GLOBAL_INT].start \
            or address > self.address_ranges[AllocCategory.CONSTANT].end:
            raise ValueError("Invalid address")
        elif address < self.address_ranges[AllocCategory.GLOBAL_INT].end:
            return "int"
        elif address < self.address_ranges[AllocCategory.GLOBAL_FLOAT].end:
            return "float"
        elif address < self.address_ranges[AllocCategory.LOCAL_INT].end:
            return "int"
        elif address < self.address_ranges[AllocCategory.LOCAL_FLOAT].end:
            return "float"
        elif address < self.address_ranges[AllocCategory.TEMP_INT].end:
            return "int"
        elif address < self.address_ranges[AllocCategory.TEMP_FLOAT].end:
            return "float"
        elif address < self.address_ranges[AllocCategory.CONSTANT].end:
            constant = self.constants.get(address)
            if constant is None:
                raise ValueError(f"Address {address} does not exist in constants")
            if isinstance(constant, str):
                return "str"
            if isinstance(constant, int):
                return "int"
            if isinstance(constant, float):
                return "float"
            else:
                raise ValueError(f"Invalid constant type: {type(constant)}")
        else:
            raise ValueError(f"Invalid address: {address}")