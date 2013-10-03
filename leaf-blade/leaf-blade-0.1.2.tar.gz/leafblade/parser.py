from leafblade.utilities import CodeBlock, escape_content, escape_attribute_value

class SyntaxError(SyntaxError):
	pass

class Node:
	def __init__(self, indent, parent):
		self.indent = indent
		self.parent = parent
		self.children = []

		if parent:
			parent.add_child(self)

	def add_child(self, child):
		self.children.append(child)

class RootNode(Node):
	pass

class NamedNode(Node):
	def __init__(self, indent, parent, name):
		super().__init__(indent, parent)
		self.name = name

class ElementNode(NamedNode):
	pass

class AttributeNode(NamedNode):
	value = None

	def __init__(self, indent, parent, name):
		super().__init__(indent, parent, name)
		self.children = None

	def add_child(self, child):
		raise SyntaxError("Attributes cannot have children")

class StringNode(Node):
	def __init__(self, indent, parent):
		super().__init__(indent, parent)
		self.content = CodeBlock()
		self.children = None

	def add_child(self, child):
		raise SyntaxError("Strings cannot have children")

class CodeNode(Node):
	code = ""

class Parser:
	line = 1
	offset = 0
	current_line = ""
	current_indent = 0

	def __init__(self, **kwargs):
		self.filename = kwargs.get("filename", "<string>")
		self.tree = RootNode(-1, None)
		self.context = self.tree

	def content(self, c):
		if c == "\n":
			self.current_indent = 0
			return self.indent
		if c == "#":
			return self.comment
		if c == "%":
			self.context = CodeNode(self.current_indent, self.context)
			return self.code
		if c == "!":
			if isinstance(self.context, AttributeNode):
				raise SyntaxError("Attributes cannot have raw strings as values")

			return self.raw_string
		if c == '"':
			string = StringNode(self.current_indent, None)
			string.parent = self.context

			if isinstance(self.context, AttributeNode):
				self.context.value = string
				self.string_escape = escape_attribute_value
			else:
				self.context.children.append(string)
				self.string_escape = escape_content

			self.context = string

			return self.string
		if c.isspace():
			return self.content
		if c.isalpha():
			self.current_identifier = ""
			return self.identifier(c)

		raise SyntaxError("Unexpected {!r}".format(c))

	def comment(self, c):
		if c == "\n":
			return self.content(c)

		return self.comment

	def code(self, c):
		if c == "\n":
			return self.content(c)

		self.context.code += c
		return self.code

	def indent(self, c):
		if c == "\n":
			# TODO: Print trailing whitespace warning if current_indent > 0?
			self.current_indent = 0
			return self.indent

		if c != "\t":
			while self.current_indent <= self.context.indent:
				self.context = self.context.parent

			if self.current_indent > self.context.indent + 1:
				raise SyntaxError("Excessive indent")

			return self.content(c)

		self.current_indent += 1
		return self.indent

	def identifier(self, c):
		if c == ":":
			return self.colon
		if c == "-" or c.isalnum():
			self.current_identifier += c
			return self.identifier

		special = special_elements.get(self.current_identifier)
		if special:
			return special(self, c)

		self.context = ElementNode(self.current_indent, self.context, self.current_identifier)
		return self.content(c)

	def colon(self, c):
		if c.isalpha():
			self.current_identifier += ":" + c
			return self.identifier(c)

		self.context = AttributeNode(self.current_indent, self.context, self.current_identifier)
		return self.content(c)

	def string(self, c):
		if c == '"':
			self.context = self.context.parent

			if isinstance(self.context, AttributeNode):
				self.context = self.context.parent

			return self.content
		if c == "\\":
			return self.escape
		if c == "#":
			return self.enter_interpolation

		self.context.content.add_text(c, self.string_escape)
		return self.string

	def raw_string(self, c):
		if c != '"':
			raise SyntaxError("Expected string")

		self.context = StringNode(None, self.context)
		self.string_escape = None

		return self.string

	def escape(self, c):
		if c != "'":
			self.context.content.add_text("\\", self.string_escape)

		self.context.content.add_text(c, self.string_escape)
		return self.string

	def enter_interpolation(self, c):
		if c == "{":
			self.current_expression = ""
			return self.interpolation

		self.context.content.add_text("#" + c, self.string_escape)
		return self.string

	def interpolation(self, c):
		if c == "}":
			self.context.content.add_expression(self.current_expression, self.string_escape)
			return self.string

		self.current_expression += c
		return self.interpolation

	state = content

	def feed(self, text):
		try:
			for i, c in enumerate(text):
				if c == "\n":
					self.line += 1
					self.offset = 0
					self.current_line = text[i+1:].partition("\n")[0]
				else:
					self.offset += 1

				self.state = self.state(c)

			if c != "\n":
				self.state("\n")
		except SyntaxError as error:
			error.filename = self.filename
			error.lineno = self.line
			error.offset = self.offset
			error.text = self.current_line
			raise

def parse(template, **kwargs):
	parser = Parser(**kwargs)
	parser.feed(template)
	return parser.tree

special_elements = {}

def special(name):
	def add_special(handler):
		special_elements[name] = handler
		return handler

	return add_special
