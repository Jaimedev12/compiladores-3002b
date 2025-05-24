from typing import Union, Optional, Any, List, Dict
from dataclasses import dataclass, field
from node_dataclasses import Param, Vars, Body, VariableType, Function
from MemoryManager import MemoryManager, AllocCategory

@dataclass
class AllocationTracker:
    local_int: int = 0
    local_float: int = 0
    temp_int: int = 0
    temp_float: int = 0

@dataclass
class FunctionRegister:
    name: str
    param_types: List[VariableType]
    start_quad: int = 0
    alloc_tracker: AllocationTracker = field(default_factory=AllocationTracker)

class FunctionTable:
    def __init__(self, memory_manager: MemoryManager):
        self.functions: Dict[str, FunctionRegister] = dict()
        self.memory_manager = memory_manager

    def add_function(self, func: Function, start_quad: int = 0) -> None:

        if func.id in self.functions:
            raise ValueError(f"Function {func.id} already exists in FunctionTable.")
        
        param_types: List[VariableType] = [param.type_ for param in func.params]
        
        self.functions[func.id] = FunctionRegister(
            name=func.id,
            param_types=param_types,
            start_quad=start_quad,
            alloc_tracker=AllocationTracker()
        )

    def get_function(self, name: str) -> Optional[FunctionRegister]:
        return self.functions.get(name)
    
    def update_function(
            self, 
            name: str, 
            param_types: Optional[List[VariableType]] = None, 
            start_quad: Optional[int] = None
        ):

        if name not in self.functions:
            raise ValueError(f"Function {name} not found in FunctionTable.")

        if param_types is not None:
            self.functions[name].param_types = param_types
        if start_quad is not None:
            self.functions[name].start_quad = start_quad

    def update_allocation_tracker(self, name: str) -> None:

        if name not in self.functions:
            raise ValueError(f"Function {name} not found in FunctionTable.")
        
        local_int = self.memory_manager.address_ranges[AllocCategory.LOCAL_INT].current - self.memory_manager.address_ranges[AllocCategory.LOCAL_INT].start
        local_float = self.memory_manager.address_ranges[AllocCategory.LOCAL_FLOAT].current - self.memory_manager.address_ranges[AllocCategory.LOCAL_FLOAT].start
        temp_int = self.memory_manager.address_ranges[AllocCategory.TEMP_INT].current - self.memory_manager.address_ranges[AllocCategory.TEMP_INT].start
        temp_float = self.memory_manager.address_ranges[AllocCategory.TEMP_FLOAT].current - self.memory_manager.address_ranges[AllocCategory.TEMP_FLOAT].start

        self.functions[name].alloc_tracker.local_int = local_int
        self.functions[name].alloc_tracker.local_float = local_float
        self.functions[name].alloc_tracker.temp_int = temp_int
        self.functions[name].alloc_tracker.temp_float = temp_float
