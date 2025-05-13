from typing import Union, Optional, Any, List, Dict
from dataclasses import dataclass
from node_dataclasses import Param, Vars, Body
from vdir_classes import MemoryManager, VariableType

@dataclass
class Symbol:
    name: str
    data_type: str
    vdir: int
    value: Optional[Union[int, float]] = None
    category: str = "var"
    param_index: Optional[int] = None

class Scope:
    def __init__(self, name: str, memory_manager: MemoryManager, body=None):
        self.name = name
        self.symbols: Dict[str, Symbol] = {}
        self.symbols_v_dir: Dict[int, Symbol]= {}
        self.params: List[Symbol] = []
        self.body: Optional[Body]= body
        self.memory_manager = memory_manager
        self.current_local_vdir = 0
    
    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the scope."""
        if symbol.name in self.symbols:
            raise ValueError(f"Symbol {symbol.name} already exists in {self.name}.")
        self.symbols[symbol.name] = symbol
        self.symbols_v_dir[symbol.vdir] = symbol
        
    def add_param(self, symbol: Symbol) -> None:
        """Add a parameter to the scope."""
        if symbol.name in self.params:
            raise ValueError(f"Parameter {symbol.name} already exists in {self.name}.")
        self.params.append(symbol)
        self.symbols[symbol.name] = symbol
        self.symbols_v_dir[symbol.vdir] = symbol

    

class SymbolTable:
    def __init__(self, memory_manager: MemoryManager):
        self.scopes: Dict[str, Scope] = {}
        self.add_scope(Scope(name="global", memory_manager=memory_manager, body=None))
        
    def get_scope(self, name: str) -> Scope:
        if name not in self.scopes:
            raise ValueError(f"Scope {name} not found.")
        return self.scopes[name]
    
    def get_variable(self, v_dir: int) -> Symbol:
        """Get a variable from the specified directory."""
        for scope in self.scopes.values():
            for symbol in scope.symbols.values():
                if symbol.category == "var" and symbol.vdir == v_dir:
                    return symbol
                
        raise ValueError(f"Variable with directory {v_dir} not found.")

    def get_variable_by_name(self, name: str, scope_name: str) -> Optional[Symbol]:
        """Get a symbol from the specified scope."""
        local_scope = self.get_scope(scope_name)
        global_scope = self.get_scope("global")
        if name in local_scope.symbols:
            return local_scope.symbols[name]
        elif name in global_scope.symbols:
            return global_scope.symbols[name]
        else:
            raise ValueError(f"Symbol {name} not found in {scope_name} or global scope.")
    
    def get_parameter(self, param_index: int, function_name: str):
        """Get a parameter from the specified function scope."""
        function_scope = self.get_scope(function_name)
        
        if len(function_scope.params) <= param_index:
            raise ValueError(f"Function {function_name} only has {len(function_scope.params)} parameters.")
        
        return function_scope.params[param_index]
            
    
    def get_symbol(self, name: str, scope_name: str) -> Symbol:
        """Get a symbol from the specified scope."""
        local_scope = self.get_scope(scope_name)
        global_scope = self.get_scope("global")
        
        param_names = [param.name for param in local_scope.params]
        for i, param_name in enumerate(param_names):
            if param_name == name:
                return local_scope.params[i]
        
        if name in local_scope.symbols:
            return local_scope.symbols[name]
        elif name in global_scope.symbols:
            return global_scope.symbols[name]
        else:
            raise ValueError(f"Symbol {name} not found in {scope_name} or global scope.")
    
    def get_variable_type(self, name: str, scope_name: str) -> Optional[str]:
        """Get the type of a variable in the specified scope."""
        var = self.get_variable_by_name(name, scope_name)
        return var.data_type if var else None

    def add_scope(self, scope: Scope) -> None:
        if scope.name in self.scopes:
            raise ValueError(f"Scope {scope.name} already exists.")
        self.scopes[scope.name] = scope
        
    def add_symbol(self, symbol: Symbol, scope_name: str) -> None:
        scope = self.get_scope(scope_name)
        scope.add_symbol(symbol)
        
    def add_variable(self, name: str, data_type: str, value: Any = None, scope_name: str = "global") -> int:
        """Add a variable to the specified scope."""
        vdir = 0
        if scope_name == "global":
            if data_type == "int":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.GLOBAL_INT)
            elif data_type == "float":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.GLOBAL_FLOAT)
            else:
                raise ValueError(f"Invalid data type {data_type} for global variable.")

        else:
            if data_type == "int":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.LOCAL_INT, local_name=scope_name)
            elif data_type == "float":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.LOCAL_FLOAT, local_name=scope_name)
            else:
                raise ValueError(f"Invalid data type {data_type} for local variable.")

        variable = Symbol(name=name, data_type=data_type, value=value, category="var", vdir=vdir)
        self.add_symbol(variable, scope_name=scope_name)
        return variable.vdir
    
    def add_parameter(self, name: str, data_type: str, scope_name: str, param_index: int) -> int:
        """Add a parameter to the specified scope."""

        vdir = 0
        if scope_name == "global":
            if data_type == "int":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.GLOBAL_INT)
            elif data_type == "float":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.GLOBAL_FLOAT)
            else:
                raise ValueError(f"Invalid data type {data_type} for global variable.")

        else:
            if data_type == "int":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.LOCAL_INT, local_name=scope_name)
            elif data_type == "float":
                vdir = self.scopes[scope_name].memory_manager.allocate(var_type=VariableType.LOCAL_FLOAT, local_name=scope_name)
            else:
                raise ValueError(f"Invalid data type {data_type} for local variable.")

        param_as_symbol = Symbol(name=name, data_type=data_type, category="param", param_index=param_index, vdir=vdir)
        scope = self.get_scope(scope_name)
        scope.add_param(param_as_symbol)
        return param_as_symbol.vdir
    
    def add_function(self, name: str, params: List[Param], body, vars: Optional[Vars]) -> None:
        """Add a function as a scope"""
        self.add_scope(Scope(name, body))
        
        for i, param in enumerate(params):
            self.add_parameter(name=param.name, data_type=param.type_, scope_name=name, param_index=i)

        for var_declaration in vars.declarations if vars else []:
            for var_name in var_declaration.names:
                self.add_variable(name=var_name, data_type=var_declaration.type_, scope_name=name)

    def update_symbol_value(self, name: str, value: Any, scope_name: str) -> None:
        """Update the value of a symbol in the specified scope."""
        local_scope = self.get_scope(scope_name)
        global_scope = self.get_scope("global")
        
        param_names = [param.name for param in local_scope.params]
        for i, param_name in enumerate(param_names):
            if param_name == name:
                local_scope.params[i].value = value
                return
        
        if name in local_scope.symbols:
            local_scope.symbols[name].value = value
            
        elif name in global_scope.symbols:
            global_scope.symbols[name].value = value
            
        else:
            raise ValueError(f"Symbol {name} not found in {scope_name} or global scope.")

    def update_parameter_value(self, param_index: int, value: Any, function_name: str) -> None:
        function_scope = self.get_scope(function_name)
        
        if len(function_scope.params) <= param_index:
            raise ValueError(f"Function {function_name} only has {len(function_scope.params)} parameters.")
        
        function_scope.params[param_index].value = value

    def is_symbol_declared(self, name: str, scope_name: str) -> bool:
        local_scope = self.get_scope(scope_name)
        global_scope = self.get_scope("global")
        
        for local_param in local_scope.params:
            if local_param.name == name:
                return True
        for global_param in global_scope.params:
            if global_param.name == name:
                return True

        found_in_local = name in local_scope.symbols
        found_in_global = name in global_scope.symbols
        return found_in_local or found_in_global
    
    def is_function_declared(self, name: str) -> bool:
        return name in self.scopes and self.scopes[name].body is not None
    
    def clean_params(self, function_name: str) -> None:
        function_scope = self.get_scope(function_name)
        for param in function_scope.params:
            param.value = None

    def to_string(self) -> str:
        """Return a string representation of the symbol table."""
        result: str = ""
        for scope_name, scope in self.scopes.items():
            result += f"Scope: {scope_name}\n"
            for symbol in scope.symbols.values():
                result += f"  {symbol.name}: {symbol.data_type} = {symbol.value}\n"
            for param in scope.params:
                result += f"  Param: {param.name}: {param.data_type} = {param.value}\n"
        return result
    
    