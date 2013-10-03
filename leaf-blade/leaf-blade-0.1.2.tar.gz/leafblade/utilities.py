void_tags = {
	"area", "base", "br", "col", "command", "embed", "hr", "img", "input",
	"keygen", "link", "meta", "param", "source", "track", "wbr"
}

def escape_literal(text):
	return text.replace("\n", r"\n").replace("\r", r"\r").replace("'", r"\'")

try:
	from leafblade_escape import escape_content, escape_attribute_value
except ImportError as e:
	def escape_content(text):
		return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

	def escape_attribute_value(text):
		return text.replace("&", "&amp;").replace('"', "&quot;")

class CodeBlock:
	def __init__(self):
		self.parts = []

	def add_text(self, text, escape_function):
		self.parts.append(("text", text, escape_function))

	def add_expression(self, expression, escape_function):
		self.parts.append(("expression", expression, escape_function))

	def add_code(self, code):
		self.parts.append(("code", code, None))

	def add_part(self, part):
		self.parts.extend(part.parts)

	def indent(self):
		self.parts.append(("indent", None, None))

	def unindent(self):
		self.parts.append(("unindent", None, None))

	def join(self, state="code"):
		code = ""
		indent_level = 0

		def indent():
			return "\t" * indent_level

		for t, part, escape_function in self.parts:
			if t == "text":
				if state == "expression":
					code += ")\n" + indent() + "__write('"
				elif state == "code":
					code += indent() + "__write('"

				if escape_function:
					code += escape_literal(escape_function(part))
				else:
					code += escape_literal(part)
			elif t == "expression":
				if state == "text":
					code += "')\n" + indent() + "__write("
				elif state == "code":
					code += indent() + "__write("

				if escape_function:
					code += escape_function.__name__ + "(str((" + part + ")))"
				else:
					code += "str((" + part + "))"
			elif t == "code":
				if state == "text":
					code += "')\n"
				elif state == "expression":
					code += ")\n"

				code += indent() + part + "\n"
			else:
				if state == "text":
					code += "')\n"
				elif state == "expression":
					code += ")\n"

				if t == "indent":
					indent_level += 1
				elif t == "unindent":
					indent_level -= 1
				else:
					raise ValueError("Unrecognized type {type!r}".format(type=t))

				state = "code"
				continue

			state = t

		if state == "text":
			code += "')\n"
		elif state == "expression":
			code += ")\n"

		return code

class TemplateData:
	pass
