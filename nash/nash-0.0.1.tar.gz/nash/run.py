import sys
from . import parser as parser
from . import interpreter as interpret

if __name__ == "__main__":
    program = " ".join(sys.argv[1:])
    p = parser.Parser()
    i = interpret.Interpreter()
    ast = p.parse(program)
    print(i.visit(ast))
