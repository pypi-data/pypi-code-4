from types import ModuleType
from leafblade.utilities import CodeBlock, escape_content, escape_attribute_value, void_tags
from leafblade.parser import ElementNode, AttributeNode, StringNode, CodeNode

class Context:
	def __init__(self, attributes=None, content=None):
		self.attributes = attributes
		self.content = content

def compile_node(node, context):
	for special, callback in special_elements.items():
		if isinstance(node, special):
			return callback(node, context)

	if isinstance(node, ElementNode):
		if node.name in special_elements:
			return special_elements[node.name](node, context)

		new_context = Context(attributes=CodeBlock())
		is_void = node.name in void_tags # TODO: Require lowercase?

		if not is_void:
			new_context.content = CodeBlock()

		context.content.add_text("<" + node.name, None)

		for child in node.children:
			compile_node(child, new_context)

		context.content.add_part(new_context.attributes)
		context.content.add_text(">", None)

		if not is_void:
			context.content.add_part(new_context.content)
			context.content.add_text("</" + node.name + ">", None)
	elif isinstance(node, AttributeNode):
		context.attributes.add_text(" " + node.name, None)

		if node.value:
			context.attributes.add_text('="', None)
			context.attributes.add_part(node.value.content)
			context.attributes.add_text('"', None)
	elif isinstance(node, StringNode):
		context.content.add_part(node.content)
	elif isinstance(node, CodeNode):
		context.content.add_code(node.code.lstrip())

		if node.children:
			context.content.indent()
			for child in node.children:
				compile_node(child, context)
			context.content.unindent()
	elif node.children:
		for child in node.children:
			compile_node(child, context)

def compile_tree(tree, **kwargs):
	code = CodeBlock()

	compiled_code = CodeBlock()
	compile_node(tree, Context(content=compiled_code))

	if all(part[0] == "text" for part in compiled_code.parts):
		code.add_code("static = " + repr("".join(part[1] for part in compiled_code.parts)))

		code.add_code("def write(__write, __data):")
		code.indent()
		code.add_code("__write(static)")
		code.unindent()

		code.add_code("def render(__data):")
		code.indent()
		code.add_code("return static")
		code.unindent()
	else:
		code.add_code("from leafblade.utilities import TemplateData, escape_content, escape_attribute_value")

		code.add_code("def write(__write, __data):")
		code.indent()
		code.add_code("data = TemplateData()")
		code.add_code("data.__dict__.update(__data)")
		code.add_part(compiled_code)
		code.unindent()

		code.add_code("def render(__data):")
		code.indent()
		code.add_code("output = []")
		code.add_code("write(output.append, __data)")
		code.add_code("return ''.join(output)")
		code.unindent()

	source = code.join()

	filename = kwargs.get("filename", "<string>")
	compiled = compile(source, filename, "exec")
	module = ModuleType(filename)
	exec(compiled, module.__dict__)

	return module

special_elements = {}

def special(t):
	def add_special(handler):
		special_elements[t] = handler
		return handler

	return add_special
