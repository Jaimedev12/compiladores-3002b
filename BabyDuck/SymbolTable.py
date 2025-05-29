from typing import Union, Optional, Any, List, Dict
from dataclasses import dataclass
from util_dataclasses import Param, Body, VariableType, AllocCategory, Symbol
from MemoryManager import MemoryManager


class Scope:
    def __init__(self, name: str, starting_quad: int, body: Optional[Body] = None):
        self.name = name
        self.symbols: Dict[str, Symbol] = {}
        self.symbols_by_vdir: Dict[int, Symbol]= {}
        self.param_list: List[Symbol] = []
        self.body: Optional[Body] = body
        self.starting_quad: int = starting_quad

    def add_symbol(self, symbol: Symbol) -> None:
        """Add any symbol to the scope."""
        if symbol.name in self.symbols:
            raise ValueError(f"Symbol {symbol.name} already exists in {self.name}.")
        
        self.symbols[symbol.name] = symbol
        self.symbols_by_vdir[symbol.vdir] = symbol
        
        if symbol.is_param:
            self.param_list.append(symbol)


class SymbolTable:
    def __init__(self, memory_manager: MemoryManager):
        self.scopes: Dict[str, Scope] = {}
        self.add_scope(Scope(name="global", starting_quad=0, body=None))
        self.memory_manager = memory_manager

    def _allocate_vdir(self, data_type: str, scope_name: str) -> int:
        """Internal helper to allocate virtual directories consistently"""
        if scope_name == "global":
            category = AllocCategory.GLOBAL_INT if data_type == "int" else AllocCategory.GLOBAL_FLOAT
        else:
            category = AllocCategory.LOCAL_INT if data_type == "int" else AllocCategory.LOCAL_FLOAT
            
        if data_type not in ["int", "float"]:
            raise ValueError(f"Invalid data type {data_type}")
            
        return self.memory_manager.allocate(var_type=category, local_name=scope_name)

    def get_scope(self, name: str) -> Scope:
        if name not in self.scopes:
            raise ValueError(f"Scope {name} not found.")
        return self.scopes[name]    
    
    def get_symbol(self, identifier: Union[str, int], scope_name: str = "global") -> Symbol:
        """Unified symbol lookup in local and global scopes
        
        Args:
            identifier: Either name (str) or vdir (int)
            scope_name: Current scope to check first
        """
        local_scope = self.get_scope(scope_name)
        global_scope = self.get_scope("global")
        
        by_name = isinstance(identifier, str)
        # Check local and global scopes
        if by_name:
            # By name lookup
            if identifier in local_scope.symbols:
                return local_scope.symbols[identifier]
            elif identifier in global_scope.symbols:
                return global_scope.symbols[identifier]
        else:
            # By vdir lookup
            if identifier in local_scope.symbols_by_vdir:
                return local_scope.symbols_by_vdir[identifier]
            elif identifier in global_scope.symbols_by_vdir:
                return global_scope.symbols_by_vdir[identifier]

        raise ValueError(f"Symbol {identifier} not found in {scope_name} or global scope.")

    def add_scope(self, scope: Scope) -> None:
        if scope.name in self.scopes:
            raise ValueError(f"Scope {scope.name} already exists.")
        self.scopes[scope.name] = scope
        
    def add_symbol(self, symbol: Symbol, scope_name: str) -> None:
        scope = self.get_scope(scope_name)
        if symbol.vdir == 0:
            symbol.vdir = self._allocate_vdir(symbol.data_type, scope_name)
        scope.add_symbol(symbol)

    def add_symbol_by_attrs(
            self, 
            name: str, 
            data_type: VariableType, 
            value: Any = None, 
            scope_name: str = "global", 
            is_param: bool = False, 
            param_index: Optional[int] = None
        ) -> int:
        """Add a symbol to the specified scope."""
        vdir = self._allocate_vdir(data_type, scope_name)

        symbol = Symbol(name=name, data_type=data_type, value=value, vdir=vdir, is_param=is_param, param_index=param_index)
        self.add_symbol(symbol, scope_name=scope_name)
        return symbol.vdir

    def add_function(self, name: str, starting_quad: int, params: List[Param], body: Optional[Body] = None) -> None:
        """Add a function as a scope"""
        self.add_scope(Scope(name, starting_quad=starting_quad, body=body))

        for i, param in enumerate(params):
            self.add_symbol_by_attrs(
                name=param.name,
                data_type=param.type_,
                scope_name=name,
                is_param=True,
                param_index=i
            )

    def is_symbol_declared(self, name: str, scope_name: str) -> bool:
        local_scope = self.get_scope(scope_name)
        global_scope = self.get_scope("global")
        
        for local_param in local_scope.param_list:
            if local_param.name == name:
                return True
        for global_param in global_scope.param_list:
            if global_param.name == name:
                return True

        found_in_local = name in local_scope.symbols
        found_in_global = name in global_scope.symbols
        return found_in_local or found_in_global
    
    def is_function_declared(self, name: str) -> bool:
        return name in self.scopes and self.scopes[name].body is not None

    def to_string(self) -> str:
        """Return a string representation of the symbol table."""
        result: str = ""
        for scope_name, scope in self.scopes.items():
            result += f"Scope: {scope_name}\n"
            for symbol in scope.symbols.values():
                result += f"  {symbol.name} - {symbol.vdir}: {symbol.data_type} = {symbol.value}\n"
            for param in scope.param_list:
                result += f"  Param: {param.name} - {param.vdir}: {param.data_type} = {param.value}\n"
        return result
    
    