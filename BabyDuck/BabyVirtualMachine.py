import sys
import pickle
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

# Import the same dataclasses to ensure compatibility
from util_dataclasses import Quad, AllocCategory, Operations, ConstantValue
from MemoryManager import MemoryManager
from read_obj import read_obj_file, ObjData

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

    def get_memory_value(self, address: int) -> Any:
        """Get a value from the appropriate memory segment"""
        if address >= 7000:  # Constants
            if address in self.constants:
                return self.constants[address]
            raise ValueError(f"Undefined constant at address {address}")
            
        elif address >= 6000:  # Temp float
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                if address in ar.temp_memory:
                    return ar.temp_memory[address]
            raise ValueError(f"Undefined temp float at address {address}")
            
        elif address >= 5000:  # Temp int
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                if address in ar.temp_memory:
                    return ar.temp_memory[address]
            raise ValueError(f"Undefined temp int at address {address}")
            
        elif address >= 4000:  # Local float
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                if address in ar.local_memory:
                    return ar.local_memory[address]
            raise ValueError(f"Undefined local float at address {address}")
            
        elif address >= 3000:  # Local int
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                if address in ar.local_memory:
                    return ar.local_memory[address]
            raise ValueError(f"Undefined local int at address {address}")
            
        elif address >= 2000:  # Global float
            if address in self.global_memory:
                return self.global_memory[address]
            raise ValueError(f"Undefined global float at address {address}")
            
        elif address >= 1000:  # Global int
            if address in self.global_memory:
                return self.global_memory[address]
            raise ValueError(f"Undefined global int at address {address}")
            
        else:
            raise ValueError(f"Invalid memory address: {address}")

    def set_memory_value(self, address: int, value: Any) -> None:
        """Store a value in the appropriate memory segment"""
        if address >= 7000:  # Constants
            raise ValueError(f"Cannot modify constant at address {address}")
            
        elif address >= 6000:  # Temp float
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                ar.temp_memory[address] = float(value)
            else:
                raise ValueError("No active function context for temp float")
            
        elif address >= 5000:  # Temp int
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                ar.temp_memory[address] = int(value)
            else:
                raise ValueError("No active function context for temp int")
            
        elif address >= 4000:  # Local float
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                ar.local_memory[address] = float(value)
            else:
                raise ValueError("No active function context for local float")
            
        elif address >= 3000:  # Local int
            if len(self.call_stack) > 0:
                ar = self.call_stack[-1]
                ar.local_memory[address] = int(value)
            else:
                raise ValueError("No active function context for local int")
            
        elif address >= 2000:  # Global float
            self.global_memory[address] = float(value)
            
        elif address >= 1000:  # Global int
            self.global_memory[address] = int(value)
            
        else:
            raise ValueError(f"Invalid memory address: {address}")
    
    def run(self) -> None:
        """Execute the program"""
        self.instruction_pointer = 0
        
        while self.instruction_pointer < len(self.quads):
            quad = self.quads[self.instruction_pointer]
            
            # print(f"Executing quad {self.instruction_pointer}: {quad}")
            # print(self.call_stack[-1].local_memory)

            if quad.op_vdir in self.operations:
                self.operations[quad.op_vdir](quad)
            else:
                raise ValueError(f"Unknown operation code: {quad.op_vdir}")
                
            if quad.op_vdir not in [Operations.GOTO.value, Operations.GOTOF.value, 
                                   Operations.GOSUB.value, Operations.ENDFUNC.value,
                                   Operations.END.value]:
                self.instruction_pointer += 1

    def _op_plus(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for addition")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = val1 + val2
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_minus(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for subtraction")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = val1 - val2
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_mult(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for multiplication")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = val1 * val2
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_div(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for division")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        if val2 == 0:
            raise ZeroDivisionError("Division by zero")
        result = val1 / val2
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_less_than(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for less than comparison")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = 1 if val1 < val2 else 0
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_greater_than(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for greater than comparison")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = 1 if val1 > val2 else 0
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_not_equal(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None or quad.storage_vdir is None:
            raise ValueError("Both vdir1 and vdir2 must be provided for not equal comparison")
        val1 = self.get_memory_value(quad.vdir1)
        val2 = self.get_memory_value(quad.vdir2)
        result = 1 if val1 != val2 else 0
        self.set_memory_value(quad.storage_vdir, result)
    
    def _op_assign(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None:
            raise ValueError("vdir1 and vdir2 must be provided for assignment")
        val = self.get_memory_value(quad.vdir2)
        self.set_memory_value(quad.vdir1, val)
    
    def _op_print(self, quad: Quad) -> None:
        if quad.vdir1 is None:
            raise ValueError("vdir1 must be provided for print operation")
        val = self.get_memory_value(quad.vdir1)
        print(val)
    
    def _op_gotof(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.vdir2 is None:
            raise ValueError("vdir1 and vdir2 must be provided for goto-if-false operation")
        
        condition = self.get_memory_value(quad.vdir1)
        if condition == 0:  # If condition is false
            self.instruction_pointer = quad.vdir2
        else:
            self.instruction_pointer += 1
    
    def _op_goto(self, quad: Quad) -> None:
        if quad.vdir1 is None:
            raise ValueError("vdir1 must be provided for goto operation")
        self.instruction_pointer = quad.vdir1
    
    def _op_end(self, quad: Quad) -> None:
        self.instruction_pointer = len(self.quads)
    
    def _op_alloc(self, quad: Quad) -> None:
        # Initialize a new function activation, but don't push it yet
        # We'll do that in _op_gosub after parameters are processed
        # Just advance to next instruction for now
        pass
    
    def _op_param(self, quad: Quad) -> None:
        if quad.vdir1 is None:
            raise ValueError("vdir1 must be provided for param operation")
        
        val = self.get_memory_value(quad.vdir1)
        if len(self.call_stack) > 0:
            self.call_stack[-1].parameters.append(val)
    
    def _op_gosub(self, quad: Quad) -> None:
        if quad.vdir1 is None or quad.label is None:
            raise ValueError("vdir1 and label must be provided for gosub operation")
        function_name = quad.label
        function_scope = self.functions[function_name]
        
        ar = ActivationRecord(function_name, self.instruction_pointer + 1)
        
        current_params = self.call_stack[-1].parameters
        self.call_stack[-1].parameters = []  # Clear for next call
        
        for i, param in enumerate(function_scope.param_list):
            if i < len(current_params):
                ar.local_memory[param.vdir] = current_params[i]
        
        self.call_stack.append(ar)
        
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