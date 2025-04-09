from lark import Lark, Transformer, v_args

# Load grammar from file
with open("grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser='lalr')


# Define a Transformer to evaluate the parsed expression
@v_args(inline=True)  # A decorator to simplify the method signatures
class BabyTransformer(Transformer):
    def number(self, n):
        return float(n)

    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a / b
    def neg(self, a): return -a
    def product(self, a): return float(a)

__all__ = ['parser', 'BabyTransformer']