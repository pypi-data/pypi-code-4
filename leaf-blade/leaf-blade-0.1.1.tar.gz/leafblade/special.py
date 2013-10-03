from . import parser
from . import compiler

class DoctypeNode(parser.Node):
	pass

@parser.special("doctype")
def parse_doctype(self, c):
	self.context = DoctypeNode(self.current_indent, self.context)
	return self.content(c)

@compiler.special(DoctypeNode)
def compile_doctype(node, context):
	if node.children:
		raise SyntaxError("The doctype element cannot have children")

	context.content.add_text("<!DOCTYPE html>", None)
