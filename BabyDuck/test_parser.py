from BabyTransformer import get_parser
# import lark # Import the lark module for parsing
import os # Import the os module
# pprint is no longer needed for the raw tree output
# import pprint 

import dataclasses # Import the dataclasses module
from lark import Token, Tree # Import Lark's Tree and Token if you might print raw parse trees

def pretty_print_tree(tree, indent=0):
    """Recursively prints a nested structure (like an AST) with indentation."""
    indent_str = ' ' * indent

    # Handle dataclass instances (your AST nodes)
    if dataclasses.is_dataclass(tree):
        print(f"{indent_str}{type(tree).__name__}:")
        for field in dataclasses.fields(tree):
            value = getattr(tree, field.name)
            # Print the field name
            print(f"{indent_str}  {field.name}:")
            # Recursively print the field's value with increased indentation
            pretty_print_tree(value, indent + 4)
    # Handle lists
    elif isinstance(tree, list):
        if not tree:
            print(f"{indent_str}[]")
        else:
            print(f"{indent_str}List:")
            for i, item in enumerate(tree):
                print(f"{indent_str}  [{i}]:")
                pretty_print_tree(item, indent + 4)
    # Handle tuples (less common for ASTs, but possible)
    elif isinstance(tree, tuple):
        if not tree:
            print(f"{indent_str}()")
        else:
            print(f"{indent_str}Tuple:")
            for i, item in enumerate(tree):
                print(f"{indent_str}  ({i}):")
                pretty_print_tree(item, indent + 4)
    # Handle raw Lark Trees (if printing before transformation)
    elif isinstance(tree, Tree):
         print(f"{indent_str}Tree(data={tree.data!r}):")
         for child in tree.children:
             pretty_print_tree(child, indent + 2)
    # Handle raw Lark Tokens (if printing before transformation)
    elif isinstance(tree, Token):
         print(f"{indent_str}Token({tree.type}, {tree.value!r})")
    # Handle basic types (int, float, str, bool, None)
    else:
        print(f"{indent_str}{repr(tree)}")

def test_parser():
    parser = get_parser()

    # Define the path to the input file
    input_file_path = os.path.join('.', 'test_inputs', 'simple_input.baby') # Use os.path.join for cross-platform compatibility

    # Read the content from the file
    try:
        with open(input_file_path, 'r') as f:
            test_input = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        # Parse the input but don't transform yet (or ensure transformer methods are commented out)
        parse_tree = parser.parse(test_input) 
        print(parse_tree)
        print("\n--- Pretty ---")
        pretty_print_tree(parse_tree)  # Use the pretty_print_tree function for better readability

        # If you later want to apply the transformer and print the transformed AST:
        # transformer = MyTransformer() # Assuming MyTransformer is defined in BabyTransformer
        # ast = transformer.transform(parse_tree)
        # print("\n--- Transformed AST (using pprint) ---")
        # pprint.pprint(ast, indent=2) # Use pprint for the transformed dataclass structure

    except Exception as e:
        print(f"Parsing failed: {e}")

if __name__ == "__main__":
    test_parser()