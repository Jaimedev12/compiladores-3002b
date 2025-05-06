from typing import Optional, Any, List
from dataclasses import dataclass
from node_dataclasses import Param

@dataclass
class Symbol:
    name: str
    data_type: str
    value: Optional[Any] = None
    category: str = "var"
    param_index: Optional[int] = None

class Scope:
    def __init__(self, name, body=None):
        self.name = name
        self.symbols = {}
        self.params = []
        self.body = body
    
    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the scope."""
        if symbol.name in self.symbols:
            raise ValueError(f"Symbol {symbol.name} already exists in {self.name}.")
        self.symbols[symbol.name] = symbol
        
    def add_param(self, symbol: Symbol) -> None:
        """Add a parameter to the scope."""
        if symbol.name in self.params:
            raise ValueError(f"Parameter {symbol.name} already exists in {self.name}.")
        self.params.append(symbol)

    

class SymbolTable:
    def __init__(self):
        self.scopes = {}
        self.add_scope(Scope(name="global", body=None))
        
    def get_scope(self, name: str) -> Scope:
        if name not in self.scopes:
            raise ValueError(f"Scope {name} not found.")
        return self.scopes.get(name)
    
    def get_variable(self, name: str, scope_name: str) -> Optional[Symbol]:
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
            
    
    def get_symbol(self, name: str, scope_name: str) -> Optional[Symbol]:
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
        var = self.get_variable(name, scope_name)
        return var.data_type if var else None

    def add_scope(self, scope: Scope) -> None:
        if scope.name in self.scopes:
            raise ValueError(f"Scope {scope.name} already exists.")
        self.scopes[scope.name] = scope
        
    def add_symbol(self, symbol: Symbol, scope_name: str) -> None:
        scope = self.get_scope(scope_name)
        scope.add_symbol(symbol)
        
    def add_variable(self, name: str, data_type: str, value=None, category="var", scope_name: str = "global", param_index: Optional[int] = None) -> None:
        """Add a variable to the specified scope."""
        variable = Symbol(name=name, data_type=data_type, value=value, category=category, param_index=param_index)
        self.add_symbol(variable, scope_name)
    
    def add_parameter(self, name: str, data_type: str, scope_name: str, param_index: int) -> None:
        """Add a parameter to the specified scope."""
        param_as_symbol = Symbol(name=name, data_type=data_type, category="param", param_index=param_index)
        scope = self.get_scope(scope_name)
        scope.add_param(param_as_symbol)
    
    def add_function(self, name: str, params: List[Param], body) -> None:
        """Add a function as a scope"""
        self.add_scope(Scope(name, body))
        
        for i, param in enumerate(params):
            self.add_parameter(name=param.name, data_type=param.type_, scope_name=name, param_index=i)

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
        
        found_in_local = name in local_scope.symbols
        found_in_global = name in global_scope.symbols
        return found_in_local or found_in_global
    
    def is_function_declared(self, name: str) -> bool:
        return name in self.scopes and self.scopes[name].body is not None
    
    def clean_params(self, function_name: str) -> None:
        function_scope = self.get_scope(function_name)
        function_scope.params = []
    
    