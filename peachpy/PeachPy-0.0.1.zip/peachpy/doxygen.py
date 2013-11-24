#
#        PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

import re
from collections import OrderedDict

class Documentation:
	def __init__(self, documentation):
		self.ingroup = None
		self.brief = list()
		self.summary = list()
		self.parameters = OrderedDict()
		self.retval = OrderedDict()
		self.returns = None
		self.throws = OrderedDict() 
		self.par = OrderedDict()
		self.warnings = list()
		for line in documentation.split("\n"):
			line = line.strip()
			if not line:
				continue
			elif line.startswith("@brief"):
				current_element = self.brief
				self.brief.append(line[len("@brief"):].lstrip())
			elif line.startswith("@summary"):
				current_element = self.summary
				self.summary.append(line[len("@summary"):].lstrip())
			elif line.startswith("@param"):
				direction = line.split()[0][len("@param"):]
				name = line.split()[1]
				description = [line[line.index(name) + len(name):].lstrip()] 
				current_element = description
				self.parameters[name] = (direction, description)
			elif line.startswith("@retval"):
				value = line.split()[1]
				description = [line[line.index(value) + len(value):].lstrip()]
				current_element = description
				self.retval[value] = description
			elif line.startswith("@returns"):
				description = [line[len("@returns"):].lstrip()]
				current_element = description
				self.returns = description
			elif line.startswith("@throws"):
				exception = line.split()[1]
				description = [line[line.index(exception) + len(exception):].lstrip()]
				current_element = description
				self.throws[exception] = description
			elif line.startswith("@"):
				raise ValueError("Found unknown Doxygen element: %s" % (line.split()[0]))
			else:
				current_element.append(line.strip())
		self.brief = "\n".join(self.brief)
		self.summary = "\n".join(self.summary)
		parameters = OrderedDict()
		for (name, (direction, description)) in self.parameters.items():
			parameters[name] = (direction, "\n".join(description))
		self.parameters = parameters
		retval = OrderedDict()
		for (value, description) in self.retval.items():
			retval[value] = "\n".join(description)
		self.retval = retval
		if self.returns:
			self.returns = "\n".join(self.returns)
		throws = OrderedDict()
		for (exception, description) in self.throws.items():
			throws[exception] = "\n".join(description)
		self.throws = throws

	def add_warning(self, warning):
		self.warnings.append(warning)

	def __str__(self):
		components = list()
		if self.ingroup:
			components.append("@ingroup\t" + str(self.ingroup))
		components.append("@brief\t" + self.brief)
		if self.summary:
			components.append("@summary\t" + self.summary)
		for warning in self.warnings:
			components.append("@warning\t" + warning)
		for (name, (direction, description)) in self.parameters.items():
			components.append("@param" + direction + "\t" + name + "\t" + description)
		for (value, description) in self.retval.items():
			components.append("@retval\t" + value + "\t" + description)
		for (exception, description) in self.throws.items():
			components.append("@throws\t" + exception + "\t" + description) 
		for (name, content) in self.par.items():
			components.append("@par\t" + name)
			for line in content:
				components.append("    \t" + line)
		return "\n".join(components)

	def xml_comment(self):
		components = list()
		components.append("<summary>" + self.brief + "</summary>")
		if self.summary:
			components.append("<remarks>" + self.summary + "</remarks>")
		for warning in self.warnings:
			components.append("<remarks>" + warning + "</remarks>")
		for (name, (direction, description)) in self.parameters.items():
			components.append("<param name=\"" + name + "\">" + description + "</param>")
		for (exception, description) in self.throws.items():
			components.append("<exception cref=\"" + exception + "\">" + description + "</exception>") 
		return "\n".join(components)
		