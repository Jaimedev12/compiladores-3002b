from BabyTransformer import get_parser
import lark # Import the lark module for parsing
import os # Import the os module
# pprint is no longer needed for the raw tree output
# import pprint 

def pretty_print_tree(tree, indent=0):
    """Recursively print the tree structure with indentation."""
    if isinstance(tree, list):
        print(" " * indent + "List ---")
        for item in tree:
            pretty_print_tree(item, indent+1)
    elif isinstance(tree, tuple):
        print(" " * indent + "Tuple ---")
        print(" " * indent + str(tree[0]))
        for item in tree[1:]:
            pretty_print_tree(item, indent + 2)
    elif isinstance(tree, lark.tree.Tree):
        print(" " * indent + "Tree ---")
        print(" " * indent + str(tree.data))
        for child in tree.children:
            pretty_print_tree(child, indent + 2)
    else:
        # if (isinstance(tree, str)):
        #     print(" " * indent + str(tree) + "<-- String ----")
        # elif (isinstance(tree, int)):
        #     print(" " * indent + str(tree) + "<-- Int ----")
        # elif (isinstance(tree, float)):
        #     print(" " * indent + str(tree) + "<-- Float ----")
        # elif (isinstance(tree, bool)):
        #     print(" " * indent + str(tree) + "<-- Bool ----")
        # else:
        #     print(" " * indent + str(tree) + "<-- Unknown ----")
        print(" " * indent + str(tree))

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
        # print(parse_tree.pretty()) # Use the pretty() method for nice formatting

        # If you later want to apply the transformer and print the transformed AST:
        # transformer = MyTransformer() # Assuming MyTransformer is defined in BabyTransformer
        # ast = transformer.transform(parse_tree)
        # print("\n--- Transformed AST (using pprint) ---")
        # pprint.pprint(ast, indent=2) # Use pprint for the transformed dataclass structure

    except Exception as e:
        print(f"Parsing failed: {e}")

if __name__ == "__main__":
    test_parser()