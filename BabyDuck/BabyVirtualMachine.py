import sys
import pickle
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from util_dataclasses import Quad, AllocCategory, Operations, ConstantValue
from MemoryManager import MemoryManager
from read_obj import read_obj_file, ObjData

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

class ActivationRecord:
    """Represents a function call's memory context"""
    def __init__(self, function_name: str, return_address: int):
        self.function_name = function_name
        self.return_address = return_address
        self.local_memory = {}
        self.temp_memory = {}
        self.parameters = []

class BabyVirtualMachine:
    def __init__(self, obj_data: ObjData):
        self.obj_data = obj_data
        self.quads = obj_data.quads
        self.constants = obj_data.constants
        self.functions = obj_data.functions
        
        self.global_memory: Dict[int, Any] = {}
        self.call_stack: List[ActivationRecord] = []
        
        self.instruction_pointer = 0
        
        self.operations = {
            Operations.PLUS.value: self._op_plus,
            Operations.MINUS.value: self._op_minus,
            Operations.MULT.value: self._op_mult,
            Operations.DIV.value: self._op_div,
            Operations.LESS_THAN.value: self._op_less_than,
            Operations.GREATER_THAN.value: self._op_greater_than,
            Operations.NOT_EQUAL.value: self._op_not_equal,
            Operations.ASSIGN.value: self._op_assign,
            Operations.PRINT.value: self._op_print,
            Operations.GOTOF.value: self._op_gotof,
            Operations.GOTO.value: self._op_goto,
            Operations.END.value: self._op_end,
            Operations.ALLOC.value: self._op_alloc,
            Operations.PARAM.value: self._op_param,
            Operations.GOSUB.value: self._op_gosub,
            Operations.ENDFUNC.value: self._op_endfunc
        }
        
        self.call_stack.append(ActivationRecord("global", -1))

    def get_memory_value(self, address: Optional[int]) -> Any:
        """Get a value from the appropriate memory segment"""
        if address is None:
            raise ValueError("Cannot access memory with None address")

        try:
            segment = MemorySegment.get_segment_by_address(address)
            
            if segment == MemorySegment.CONSTANT:
                if address in self.constants:
                    return self.constants[address]
                raise ValueError(f"Undefined constant at address {address}")
            
            if segment.is_local:
                if not self.call_stack:
                    raise ValueError(f"No active function context for {segment.name} memory")
                
                ar = self.call_stack[-1]
                memory = ar.temp_memory if segment in (MemorySegment.TEMP_INT, MemorySegment.TEMP_FLOAT) else ar.local_memory
                
                if address in memory:
                    return memory[address]
                raise ValueError(f"Undefined variable at address {address} in {segment.name}")
            
            else:
                if address in self.global_memory:
                    return self.global_memory[address]
                raise ValueError(f"Undefined variable at address {address} in {segment.name}")
                
        except ValueError as e:
            raise ValueError(f"Memory access error: {str(e)}")

    def set_memory_value(self, address: Optional[int], value: Any) -> None:
        """Store a value in the appropriate memory segment"""
        if address is None:
            raise ValueError("Cannot write to memory with None address")
        
        try:
            segment = MemorySegment.get_segment_by_address(address)
            
            if segment == MemorySegment.CONSTANT:
                raise ValueError(f"Cannot modify constant at address {address}")
            
            value_to_store = float(value) if segment.is_float else int(value)
            
            if segment.is_local:
                if not self.call_stack:
                    raise ValueError(f"No active function context for {segment.name} memory")
                
                ar = self.call_stack[-1]
                if segment in (MemorySegment.TEMP_INT, MemorySegment.TEMP_FLOAT):
                    ar.temp_memory[address] = value_to_store
                else:
                    ar.local_memory[address] = value_to_store
                    
            else:
                self.global_memory[address] = value_to_store
                
        except ValueError as e:
            raise ValueError(f"Memory write error: {str(e)}")
    
    def validate_operation_args(self, quad: Quad, required_args: Tuple[str, ...]) -> None:
        """Validate that required arguments are present in the quadruple"""
        for arg_name in required_args:
            if getattr(quad, arg_name) is None:
                raise ValueError(f"Missing required argument: {arg_name} for operation {Operations(quad.op_vdir).name}")
    
    def run(self) -> None:
        """Execute the program"""
        self.instruction_pointer = 0
        
        while self.instruction_pointer < len(self.quads):
            quad = self.quads[self.instruction_pointer]
            
            if quad.op_vdir in self.operations:
                try:
                    self.operations[quad.op_vdir](quad)
                except Exception as e:
                    raise RuntimeError(f"Error executing instruction {self.instruction_pointer}: {e}")
            else:
                raise ValueError(f"Unknown operation code: {quad.op_vdir}")
                
            if quad.op_vdir not in [Operations.GOTO.value, Operations.GOTOF.value, 
                                   Operations.GOSUB.value, Operations.ENDFUNC.value,
                                   Operations.END.value]:
                self.instruction_pointer += 1

    def _execute_binary_operation(self, quad: Quad, operation: Callable[[Any, Any], Any]) -> None:
        """Execute a binary operation with the given function"""
        self.validate_operation_args(quad, ('vdir1', 'vdir2', 'storage_vdir'))
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = operation(val1, val2)
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_plus(self, quad: Quad) -> None:
        self._execute_binary_operation(quad, lambda a, b: a + b)
    
    def _op_minus(self, quad: Quad) -> None:
        self._execute_binary_operation(quad, lambda a, b: a - b)
    
    def _op_mult(self, quad: Quad) -> None:
        self._execute_binary_operation(quad, lambda a, b: a * b)
    
    def _op_div(self, quad: Quad) -> None:
        self._execute_binary_operation(quad, lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ZeroDivisionError("Division by zero")))
    
    def _execute_comparison(self, quad: Quad, comparison: Callable[[Any, Any], bool]) -> None:
        """Execute a comparison operation with the given function"""
        self.validate_operation_args(quad, ('vdir1', 'vdir2', 'storage_vdir'))
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = 1 if comparison(val1, val2) else 0
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_less_than(self, quad: Quad) -> None:
        self._execute_comparison(quad, lambda a, b: a < b)
    
    def _op_greater_than(self, quad: Quad) -> None:
        self._execute_comparison(quad, lambda a, b: a > b)
    
    def _op_not_equal(self, quad: Quad) -> None:
        self._execute_comparison(quad, lambda a, b: a != b)
    
    def _op_assign(self, quad: Quad) -> None:
        self.validate_operation_args(quad, ('vdir1', 'vdir2'))
        val = self.get_memory_value(quad.vdir2)
        self.set_memory_value(quad.vdir1, val)
    
    def _op_print(self, quad: Quad) -> None:
        self.validate_operation_args(quad, ('vdir1',))
        val = self.get_memory_value(quad.vdir1)
        print(val)
    
    def _op_gotof(self, quad: Quad) -> None:
        self.validate_operation_args(quad, ('vdir1', 'vdir2'))
        condition = self.get_memory_value(quad.vdir1)
        if condition == 0:
            assert quad.vdir2 is not None, "GOTOF requires a valid vdir2"
            self.instruction_pointer = quad.vdir2
        else:
            self.instruction_pointer += 1
    
    def _op_goto(self, quad: Quad) -> None:
        self.validate_operation_args(quad, ('vdir1',))
        assert quad.vdir1 is not None, "GOTO requires a valid vdir1"
        self.instruction_pointer = quad.vdir1
    
    def _op_end(self, quad: Quad) -> None:
        self.instruction_pointer = len(self.quads)
    
    def _op_alloc(self, quad: Quad) -> None:
        # No validation needed - just a no-op for VM
        pass
    
    def _op_param(self, quad: Quad) -> None:
        self.validate_operation_args(quad, ('vdir1',))
        val = self.get_memory_value(quad.vdir1)
        if self.call_stack:
            self.call_stack[-1].parameters.append(val)
    
    def _op_gosub(self, quad: Quad) -> None:
        self.validate_operation_args(quad, ('vdir1', 'label'))
        function_name = quad.label
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not defined")
        function_scope = self.functions[function_name]
        
        ar = ActivationRecord(function_name, self.instruction_pointer + 1)
        
        current_params = self.call_stack[-1].parameters
        self.call_stack[-1].parameters = []
        
        for i, param in enumerate(function_scope.param_list):
            if i < len(current_params):
                ar.local_memory[param.vdir] = current_params[i]
        
        self.call_stack.append(ar)
        assert quad.vdir1 is not None, "GOSUB requires a valid vdir1"
        self.instruction_pointer = quad.vdir1
    
    def _op_endfunc(self, quad: Quad) -> None:
        if len(self.call_stack) <= 1:
            raise RuntimeError("Cannot return from global scope")
            
        ar = self.call_stack.pop()
        self.instruction_pointer = ar.return_address

def main():
    if len(sys.argv) < 2:
        print("Usage: python BabyVirtualMachine.py <object_file>")
        sys.exit(1)
        
    obj_file = sys.argv[1]
    if not obj_file.endswith('.obj'):
        obj_file += '.obj'
        
    try:
        obj_data = read_obj_file(obj_file)
        vm = BabyVirtualMachine(obj_data)
        print(f"Executing program: {obj_data.metadata.filename}")
        print("-" * 40)
        vm.run()
        print("\n" + "-" * 40)
        print("Program execution completed")
        
    except Exception as e:
        print(f"Execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()