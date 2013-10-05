from . import parser
from . import compiler
from . import special

class Template:
	def __init__(self, template, **kwargs):
		tree = parser.parse(template, **kwargs)
		self.template = compiler.compile_tree(tree, **kwargs)

	def render(self, data=None):
		return self.template.render(data)
