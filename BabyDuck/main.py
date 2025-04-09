import sys

from BabyTransformer import parser, BabyTransformer

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "input.baby"  # Default file

    try:
        with open(file_path, "r") as file:
            expression = file.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    tree = parser.parse(expression)
    print(tree.pretty())

    # expression = "3 + 4 * 2"
    # print_tokens(expression)
    # print("")
    # tree = parser.parse(expression)
    # print(tree)
    # print("")
    # print(tree.pretty())
    
    # result = CalcTransformer().transform(tree)
    # print(f"Result: {result}")

if __name__ == "__main__":
    main()
