#
#		PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

import re

class Type(object):
	integer_types = ['byte', 'short', 'int', 'long']
	floating_point_types = ['float', 'double']

	def __init__(self, type):
		super(Type, self).__init__()
		type_components = re.match("(byte|short|int|long|float|double)(?:\s*(\[\]))?", type)
		if type_components is None:
			raise ValueError('The type {0} is not recognized as a Java type'.format(type))
		self.primitive_type = type_components.group(1)
		self.is_array_type = bool(type_components.group(2))

	def __str__(self):
		return self.format()

	def format(self):
		text = self.primitive_type
		if self.is_array_type:
			text += "[]"
		return text

	def is_integer(self):
		if self.is_array():
			return False
		else:
			return self.primitive_type in Type.integer_types

	def is_array(self):
		return self.is_array_type

	def is_floating_point(self):
		if self.is_array():
			return False
		else:
			return self.primitive_type in Type.floating_point_types

	def get_primitive_type(self):
		return Type(self.primitive_type)

	def get_jni_analog(self):
		import peachpy.c
		if self.is_array():
			return peachpy.c.Type("j" + str(self.primitive_type) + "Array")
		else:
			return peachpy.c.Type("j" + str(self.primitive_type))

class Parameter(object):
	def __init__(self, name, jtype):
		super(Parameter, self).__init__()
		if isinstance(name, str):
			self.name = name
		else:
			raise TypeError('Parameter name must be a string')
		if isinstance(jtype, Type):
			self.type = jtype
		else:
			raise TypeError('Parameter type must be an instance of Type object')

	def __eq__(self, other):
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)

	def __str__(self):
		return self.format()

	def format(self):
		return self.get_type().format() + " " + self.get_name()

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def get_jni_analog(self):
		import peachpy.c
		return peachpy.c.Parameter(self.get_name(), self.get_type().get_jni_analog())
