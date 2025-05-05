from typing import Optional

class Symbol:
    def __init__(self, name, var_type, value=None, category="var", param_index=None):
        self.name = name
        self.var_type = var_type
        self.value = value
        self.category = category
        self.param_index = param_index

class Container:
    def __init__(self, name, body=None):
        self.name = name
        self.symbols = {}
        self.params = {}
        self.body = body

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the container."""
        if symbol.name in self.symbols:
            raise ValueError(f"Symbol {symbol.name} already exists in {self.name}.")
        self.symbols[symbol.name] = symbol

    def add_param(self, symbol: Symbol) -> None:
        """Add a parameter to the container."""
        if symbol.name in self.params:
            raise ValueError(f"Parameter {symbol.name} already exists in {self.name}.")
        self.params[symbol.name] = symbol

    def set_params_values(self, values: list) -> None:
        """Set the values of parameters in the container."""
        if len(values) != len(self.params):
            raise ValueError(f"Number of values does not match number of parameters in {self.name}.")
        
        # update params in order of their param_index
        for param in sorted(self.params.values(), key=lambda p: p.param_index):
            if param.param_index is not None:
                param.value = values[param.param_index]
            else:
                raise ValueError(f"Parameter {param.name} does not have a valid index.")

    def get_symbol(self, name: str) -> Symbol:
        """Get a symbol from the container."""
        if name in self.params:
            return self.params.get(name, None)
        elif name in self.symbols:
            return self.symbols.get(name, None)
        else:
            raise ValueError(f"Symbol {name} not found in {self.name}.")
    
    def update_symbol(self, name: str, value) -> None:
        """Update the value of a symbol in the container."""
        if name not in self.symbols and name not in self.params:
            raise ValueError(f"Symbol {name} not found in {self.name}.")
        symbol = self.get_symbol(name)
        if symbol.category == "const":
            raise ValueError(f"Cannot modify constant {name}.")
        symbol.value = value

    def is_symbol_declared(self, name: str) -> bool:
        """Check if a symbol is declared in the container."""
        return name in self.symbols or name in self.params
    
    def clean_params_values(self) -> None:
        """Reset the values of parameters in the container."""
        for param in self.params.values():
            param.value = None

class SymbolTable:
    def __init__(self):
        self.containers = {}
        self.add_container(Container("global", None))

    def get_container(self, name: str) -> Container:
        """Get a container by name."""
        if name not in self.containers:
            raise ValueError(f"Container {name} not found.")
        return self.containers.get(name)

    def add_container(self, container: Container) -> None:
        """Add a new container to the symbol table."""
        if container.name in self.containers:
            raise ValueError(f"Container {container.name} already exists.")
        self.containers[container.name] = container

    def __add_symbol(self, symbol: Symbol, containerName: str) -> None:
        """Add a symbol to the specified container."""
        container = self.get_container(containerName)
        container.add_symbol(symbol)

    def __get_symbol(self, name: str, containerName: str) -> Symbol:
        """Get a symbol from the specified container."""
        container = self.get_container(containerName)
        if container.is_symbol_declared(name):
            return container.get_symbol(name)
        else:
            container = self.containers["global"]
            if container.is_symbol_declared(name):
                return container.get_symbol(name)
            else:
                raise ValueError(f"Symbol {name} not found in {containerName} or global container.")

    def __update_symbol(self, name: str, value, containerName: str) -> None:
        """Update the value of a symbol in the specified container."""
        container = self.get_container(containerName)
        if container.is_symbol_declared(name):
            container.update_symbol(name, value)
        else:
            container = self.containers["global"]
            if container.is_symbol_declared(name):
                container.update_symbol(name, value)
            else:
                raise ValueError(f"Symbol {name} not found in {containerName} or global container.")

    def add_variable(self, name: str, var_type: str, value=None, category="var", containerName: str = "global", param_index: Optional[int] = None) -> None:
        """Add a variable to the specified container."""
        variable = Symbol(name=name, var_type=var_type, value=value, category=category, param_index=param_index)
        self.__add_symbol(variable, containerName)

    def add_parameter(self, name: str, var_type: str, containerName: str, param_index: Optional[int] = None) -> None:
        """Add a parameter to the specified container."""
        variable = Symbol(name=name, var_type=var_type, category="param", param_index=param_index)
        container = self.get_container(containerName)
        container.add_param(variable)

    def get_variable(self, name: str, containerName: str) -> Symbol:
        """Get a variable from the specified container."""
        return self.__get_symbol(name, containerName).value
    
    def get_variable_type(self, name: str, containerName: str) -> str:
        """Get the type of a variable from the specified container."""
        return self.__get_symbol(name, containerName).var_type
    
    def update_variable(self, name: str, value, containerName: str) -> None:
        """Update the value of a variable in the specified container."""
        self.__update_symbol(name, value, containerName)

    def add_function(self, name: str, params: list, body) -> None:
        """Add a function as a container"""
        self.add_container(Container(name, body))
        
        for i, param in enumerate(params):
            param_name, param_type = param
            self.add_parameter(name=param_name, var_type=param_type, containerName=name, param_index=i)
        
    def update_params_values(self, containerName: str, values: list) -> None:
        """Set the values of parameters in the specified container."""
        container = self.get_container(containerName)
        container.set_params_values(values)

    def clean_params_values(self, containerName: str) -> None:
        """Reset the values of parameters in the specified container."""
        container = self.get_container(containerName)
        container.clean_params_values()
        
    def display(self) -> None:
        """Display the contents of the symbol table."""
        for container_name, container in self.containers.items():
            print(f"Container: {container_name}")
            print("  Parameters:")
            for param_name, param in container.params.items():
                print(f"  {param_name}: {param.var_type}, {param.value}, {param.category}, {param.param_index}")
            print("  Symbols:")
            for symbol_name, symbol in container.symbols.items():
                print(f"  {symbol_name}: {symbol.var_type}, {symbol.value}, {symbol.category}, {symbol.param_index}")

    def get_str_representation(self):
        """String representation of the symbol table."""
        result = ""
        for container_name, container in self.containers.items():
            result += f"Container: {container_name}\n"
            result += "  Parameters:\n"
            for param_name, param in container.params.items():
                result += f"  {param_name}: {param.var_type}, {param.value}, {param.category}, {param.param_index}\n"
            result += "  Symbols:\n"
            for symbol_name, symbol in container.symbols.items():
                result += f"  {symbol_name}: {symbol.var_type}, {symbol.value}, {symbol.category}, {symbol.param_index}\n"
        return result