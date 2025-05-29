from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union, Tuple, Literal

class AllocCategory(Enum):
    GLOBAL_INT = 1
    GLOBAL_FLOAT = 2
    LOCAL_INT = 3
    LOCAL_FLOAT = 4
    TEMP_INT = 5
    TEMP_FLOAT = 6
    CONSTANT = 7

    @classmethod
    def get_category_from_address(cls, address: int) -> 'AllocCategory':
        for category, range_info in DATA_RANGES.items():
            if range_info.start <= address <= range_info.end:
                return category
        raise ValueError(f"Invalid memory address: {address}")
    
    @property
    def is_local(self) -> bool:
        return self in (AllocCategory.LOCAL_INT, AllocCategory.LOCAL_FLOAT, 
                       AllocCategory.TEMP_INT, AllocCategory.TEMP_FLOAT)
    
    @property
    def is_float(self) -> bool:
        return self in (AllocCategory.GLOBAL_FLOAT, AllocCategory.LOCAL_FLOAT, AllocCategory.TEMP_FLOAT)

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
    ALLOC = 13
    PARAM = 14
    CALL = 15
    ENDFUNC = 16
    GOSUB = 17

@dataclass
class AddressRange:
    start: int
    end: int
    current: int

GLOBAL_INT_START = 1000
RANGE_SIZE = 1000

DATA_STARTS = {
    AllocCategory.GLOBAL_INT: GLOBAL_INT_START,
    AllocCategory.GLOBAL_FLOAT: GLOBAL_INT_START + RANGE_SIZE,
    AllocCategory.LOCAL_INT: GLOBAL_INT_START + RANGE_SIZE * 2,
    AllocCategory.LOCAL_FLOAT: GLOBAL_INT_START + RANGE_SIZE * 3,
    AllocCategory.TEMP_INT: GLOBAL_INT_START + RANGE_SIZE * 4,
    AllocCategory.TEMP_FLOAT: GLOBAL_INT_START + RANGE_SIZE * 5,
    AllocCategory.CONSTANT: GLOBAL_INT_START + RANGE_SIZE * 6
}

DATA_RANGES = {
    AllocCategory.GLOBAL_INT: AddressRange(
        DATA_STARTS[AllocCategory.GLOBAL_INT], 
        DATA_STARTS[AllocCategory.GLOBAL_INT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.GLOBAL_INT]
    ),
    AllocCategory.GLOBAL_FLOAT: AddressRange(
        DATA_STARTS[AllocCategory.GLOBAL_FLOAT], 
        DATA_STARTS[AllocCategory.GLOBAL_FLOAT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.GLOBAL_FLOAT]
    ),
    AllocCategory.LOCAL_INT: AddressRange(
        DATA_STARTS[AllocCategory.LOCAL_INT], 
        DATA_STARTS[AllocCategory.LOCAL_INT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.LOCAL_INT]
    ),
    AllocCategory.LOCAL_FLOAT: AddressRange(
        DATA_STARTS[AllocCategory.LOCAL_FLOAT], 
        DATA_STARTS[AllocCategory.LOCAL_FLOAT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.LOCAL_FLOAT]
    ),
    AllocCategory.TEMP_INT: AddressRange(
        DATA_STARTS[AllocCategory.TEMP_INT], 
        DATA_STARTS[AllocCategory.TEMP_INT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.TEMP_INT]
    ),
    AllocCategory.TEMP_FLOAT: AddressRange(
        DATA_STARTS[AllocCategory.TEMP_FLOAT], 
        DATA_STARTS[AllocCategory.TEMP_FLOAT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.TEMP_FLOAT]
    ),
    AllocCategory.CONSTANT: AddressRange(
        DATA_STARTS[AllocCategory.CONSTANT], 
        DATA_STARTS[AllocCategory.CONSTANT] + RANGE_SIZE - 1, 
        current=DATA_STARTS[AllocCategory.CONSTANT]
    )
}

# def get_category_from_address(address: int) -> AllocCategory:
#     for category, range_info in DATA_RANGES.items():
#         if range_info.start <= address <= range_info.end:
#             return category
#     raise ValueError(f"Invalid memory address: {address}")

class MemorySegment(Enum):
    GLOBAL_INT = (1000, 1999)
    GLOBAL_FLOAT = (2000, 2999)
    LOCAL_INT = (3000, 3999)
    LOCAL_FLOAT = (4000, 4999)
    TEMP_INT = (5000, 5999)
    TEMP_FLOAT = (6000, 6999)
    CONSTANT = (7000, 7999)
    
    @classmethod
    def get_segment_by_address(cls, address: int) -> 'MemorySegment':
        for segment in cls:
            if segment.value[0] <= address <= segment.value[1]:
                return segment
        raise ValueError(f"Invalid memory address: {address}")
    
    @property
    def is_local(self) -> bool:
        return self in (MemorySegment.LOCAL_INT, MemorySegment.LOCAL_FLOAT, 
                       MemorySegment.TEMP_INT, MemorySegment.TEMP_FLOAT)
    
    @property
    def is_float(self) -> bool:
        return self in (MemorySegment.GLOBAL_FLOAT, MemorySegment.LOCAL_FLOAT, MemorySegment.TEMP_FLOAT)