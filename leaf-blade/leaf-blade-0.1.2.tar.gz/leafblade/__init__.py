from . import parser
from . import compiler
from . import special

def compile(template, **kwargs):
	tree = parser.parse(template, **kwargs)
	return compiler.compile_tree(tree, **kwargs)
