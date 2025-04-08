from lark import Lark, Transformer, v_args

# Load grammar from file
with open("grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser='lalr')

# Token inspection
def print_tokens(text):
    print("Tokens:")
    for token in parser.lex(text):
        print(f"{token.type:10} {token.value}")

# Define a Transformer to evaluate the parsed expression
@v_args(inline=True)  # A decorator to simplify the method signatures
class CalcTransformer(Transformer):
    def number(self, n):
        return float(n)

    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a / b
    def neg(self, a): return -a

# Parse and evaluate
def main():
    expression = "3 + 4 * (2 - 1)"
    print_tokens(expression)
    tree = parser.parse(expression)
    print("")
    print(tree.pretty())
    
    result = CalcTransformer().transform(tree)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
