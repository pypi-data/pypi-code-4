#
#		PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

class Type(object):
	supported_types = [	'sbyte', 'short', 'int', 'long',
						'byte', 'ushort', 'uint', 'ulong',
						'float', 'double', 'bool',
						'System.SByte', 'System.Int16', 'System.Int32', 'System.Int64', 'System.IntPtr',
						'System.Byte', 'System.UInt16', 'System.UInt32', 'System.UInt64', 'System.UIntPtr',
						'System.Single', 'System.Double', 'System.Boolean']

	def __init__(self, type):
		super(Type, self).__init__()
		for primitive_type in Type.supported_types:
			if type.startswith(primitive_type):
				self.primitive_type = primitive_type
				if type == primitive_type:
					self.is_array_type = False
					self.is_pointer_type = False
					break
				else:
					type = type[len(primitive_type):]
					if type == "*":
						self.is_array_type = False
						self.is_pointer_type = True
						break
					elif type == "[]":
						self.is_array_type = True
						self.is_pointer_type = False
						break
					else:
						raise ValueError('The type {0} is not recognized as a .Net type'.format(primitive_type + type))
		else:
			raise ValueError('The type {0} is not recognized as a .Net type'.format(type))

	def __str__(self):
		return self.format()

	def format(self):
		text = self.primitive_type
		if self.is_array():
			text += "[]"
		elif self.is_pointer():
			text += "*"
		return text

	def __ne__(self, other):
		return not(self == other)

	def __eq__(self, other):
		return isinstance(other, Type) \
			and self.primitive_type == other.primitive_type \
			and self.is_array_type == other.is_array_type \
			and self.is_pointer_type == other.is_pointer_type

	def is_array(self):
		return self.is_array_type

	def is_pointer(self):
		return self.is_pointer_type

	def is_unsigned_integer(self):
		if self.is_pointer() or self.is_array():
			return False
		else:
			return self.primitive_type in [	'byte', 'ushort', 'uint', 'ulong',
											'System.Byte', 'System.UInt16', 'System.UInt32', 'System.UInt64', 'System.UIntPtr' ] 

	def is_signed_integer(self):
		if self.is_pointer() or self.is_array():
			return False
		else:
			return self.primitive_type in [	'sbyte', 'short', 'int', 'long',
											'System.SByte', 'System.Int16', 'System.Int32', 'System.Int64', 'System.IntPtr' ] 

	def is_integer(self):
		return self.is_signed_integer() or self.is_unsigned_integer()

	def get_primitive_type(self):
		return Type(self.primitive_type)

	def get_size(self):
		if self.is_array():
			return None
		elif self.is_pointer():
			return None
		else:
			return {'sbyte' : 1,
					'short' : 2,
					'int'   : 4,
					'long'  : 8,
					'byte'  : 1,
					'ushort': 2,
					'uint'  : 4,
					'ulong' : 8,
					'float' : 4,
					'double': 8,
					'bool'  : 1,
					'System.SByte'  : 1,
					'System.Int16'  : 2,
					'System.Int32'  : 4,
					'System.Int64'  : 8,
					'System.IntPtr' : None,
					'System.Byte'   : 1,
					'System.UInt16' : 2,
					'System.UInt32' : 4,
					'System.UInt64' : 8,
					'System.UIntPtr': None,
					'System.Single' : 4,
					'System.Double' : 8,
					'System.Boolean': 1}[self.primitive_type]
		
class Parameter(object):
	def __init__(self, name, cstype, is_output = False):
		super(Parameter, self).__init__()
		self.is_output = bool(is_output)
		if isinstance(name, str):
			self.name = name
		else:
			raise TypeError('Parameter name must be a string')
		if isinstance(cstype, Type):
			self.type = cstype
		else:
			raise TypeError('Parameter type must be an instance of Type object')

	def __eq__(self, other):
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)

	def __str__(self):
		return self.format()

	def format(self, include_out_keyword = True, include_type = True, include_name = True):
		text = "out" if self.is_output and include_out_keyword else ""
		if include_type:
			if text:
				text += " "
			text += self.type.format()
		if include_name:
			if text:
				text += " "
			text += self.name
		return text

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type
