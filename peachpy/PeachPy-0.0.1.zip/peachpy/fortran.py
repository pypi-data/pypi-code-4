#
#        PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

import re

class Type(object):
	integer_types = ['INTEGER(C_INT8_T)', 'INTEGER(C_INT16_T)', 'INTEGER(C_INT32_T)', 'INTEGER(C_INT64_T)', 'INTEGER(C_SIZE_T)']
	floating_point_types = ['REAL(C_FLOAT)', 'REAL(C_DOUBLE)']
	iso_c_types = integer_types + floating_point_types
	iso_c_symbols = ['C_INT8_T', 'C_INT16_T', 'C_INT32_T', 'C_INT64_T', 'C_SIZE_T', 'C_FLOAT', 'C_DOUBLE']  

	def __init__(self, type):
		super(Type, self).__init__()
		for primitive_type in Type.iso_c_types:
			if type.startswith(primitive_type):
				self.primitive_type = primitive_type
				if type == primitive_type:
					self.dimension = None
					break
				else:
					dimension = type[len(primitive_type):]
					dimension_matcher = re.match(",\\s*DIMENSION\\((\\d+|[A-Za-z_][A-Za-z0-9_]*|\\*)\\)", dimension)
					if dimension_matcher:
						self.dimension = dimension_matcher.group(1)
						try:
							self.dimension = int(self.dimension)
						except ValueError:
							pass		
						break				
					else:
						raise ValueError('The type {0} is not recognized as a Fortran ISO_C_BINDING type'.format(type))
		else:
			raise ValueError('The type {0} is not recognized as a Fortran ISO_C_BINDING type'.format(type))

	def __str__(self):
		return self.format()

	def format(self):
		text = self.primitive_type
		if self.dimension is not None:
			text += ", DIMENSION(%s)" % self.dimension
		return text

	def is_array(self):
		return not(self.dimension is None)

	def set_dimension(self, dimension):
		if self.is_array():
			if isinstance(dimension, int):
				if dimension > 0:
					self.dimension = dimension
				else:
					raise ValueError("Dimension must be a non-negative integer")
			elif isinstance(dimension, str):
				self.dimension = dimension
			else:
				raise TypeError("Dimension must be an integer or string")
		else:
			raise ValueError("Dimension can be changed only for array types")

	def get_symbol(self):
		return {
			'INTEGER(C_INT8_T)': 'C_INT8_T',
			'INTEGER(C_INT16_T)': 'C_INT16_T',
			'INTEGER(C_INT32_T)': 'C_INT32_T',
			'INTEGER(C_INT64_T)': 'C_INT64_T',
			'INTEGER(C_SIZE_T)': 'C_SIZE_T',
			'REAL(C_FLOAT)': 'C_FLOAT',
			'REAL(C_DOUBLE)': 'C_DOUBLE'
		}[self.primitive_type]
		

class Parameter(object):
	def __init__(self, name, ftype, is_input, is_output):
		super(Parameter, self).__init__()
		if isinstance(name, str):
			self.name = name
		else:
			raise TypeError('Parameter name must be a string')
		if isinstance(ftype, Type):
			self.type = ftype
		else:
			raise TypeError('Parameter type %s is not an instance of Type object' % ftype)
		if is_input or is_output:
			self.is_input = bool(is_input)
			self.is_output = bool(is_output)
		else:
			raise TypeError('Parameter %s is neither input nor output' % name)

	def __eq__(self, other):
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)

	def __str__(self):
		return self.name

	def format(self, format_type = True, format_name = True, type_alignment = None):
		if format_type:
			if self.type.dimension is None:
				if self.is_output:
					type_string = "{0}, INTENT(OUT)".format(self.type.primitive_type)
				else:
					type_string = "{0}, VALUE".format(self.type.primitive_type)
			else:
				if self.is_input and self.is_output:
					intent_string = "INOUT"
				elif self.is_input:
					intent_string = "IN"
				else:
					intent_string = "OUT"
				type_string = "{0}, INTENT({1}), DIMENSION({2})".format(self.type.primitive_type, intent_string, self.type.dimension)
		if format_type and format_name:
			if type_alignment is None:
				return type_string + " :: " + self.name
			else:
				return (type_string + "\t:: " + self.name).expandtabs(type_alignment + 1)
		elif format_type:
			return type_string
		elif format_name:
			return self.name

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def get_size(self, abi):
		return self.type.get_size(abi)
