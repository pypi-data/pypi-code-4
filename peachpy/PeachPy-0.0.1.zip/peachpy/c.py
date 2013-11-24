#
#        PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

import re
from collections import OrderedDict

class ABI:
	def __init__(self, abi):
		from peachpy import x64, x86, arm
		if abi == 'x86':
			self.name = 'x86'
			self.pointer_size = 4
			self.general_purpose_register_size = 4
			self.int_size = 4
			self.long_size = 4
			self.long_long_size = 8
			self.stack_alignment = 4
			self.soft_float = False
			self.function_prefix = "_"
			self.callee_save_registers = [x86.ebx, x86.esi, x86.edi, x86.ebp]
			self.argument_registers = []
			self.volatile_registers = [x86.eax, x86.ecx, x86.edx,
			                           x86.mm0, x86.mm1, x86.mm2, x86.mm3, x86.mm4, x86.mm5, x86.mm6, x86.mm7,
			                           x86.xmm0, x86.xmm1, x86.xmm2, x86.xmm3, x86.xmm4, x86.xmm5, x86.xmm6, x86.xmm7]
		elif abi == 'x32':
			self.name = 'x32'
			self.pointer_size = 4
			self.general_purpose_register_size = 8
			self.int_size = 4
			self.long_size = 8
			self.long_long_size = 8
			self.stack_alignment = 16
			self.soft_float = False
			self.function_prefix = ""
			self.callee_save_registers = [x64.rbx, x64.rbp, x64.r12, x64.r13, x64.r14, x64.r15]
		elif abi == 'x64-sysv':
			self.name = 'x64-sysv'
			self.pointer_size = 8
			self.general_purpose_register_size = 8
			self.int_size = 4
			self.long_size = 8
			self.long_long_size = 8
			self.stack_alignment = 16
			self.soft_float = False
			self.function_prefix = ""
			self.callee_save_registers = [x64.rbx, x64.rbp, x64.r12, x64.r13, x64.r14, x64.r15]
			self.argument_registers = [x64.rdi, x64.rsi, x64.rdx, x64.rcx, x64.r8, x64.r9,
			                           x64.xmm0, x64.xmm1, x64.xmm2, x64.xmm3, x64.xmm4, x64.xmm5, x64.xmm6, x64.xmm7]
			self.volatile_registers = [x64.rax, x64.r10, x64.r11,
			                           x64.mm0, x64.mm1, x64.mm2, x64.mm3, x64.mm4, x64.mm5, x64.mm6, x64.mm7,
			                           x64.xmm8, x64.xmm9, x64.xmm10, x64.xmm11, x64.xmm12, x64.xmm13, x64.xmm14, x64.xmm15]
		elif abi == 'x64-ms':
			self.name = 'x64-ms'
			self.pointer_size = 8
			self.general_purpose_register_size = 8
			self.int_size = 4
			self.long_size = 4
			self.long_long_size = 8
			self.stack_alignment = 16
			self.soft_float = False
			self.function_prefix = ""
			self.callee_save_registers = [x64.rbx, x64.rsi, x64.rdi, x64.rbp, x64.r12, x64.r13, x64.r14, x64.r15,
			                              x64.xmm6, x64.xmm7, x64.xmm8, x64.xmm9, x64.xmm10, x64.xmm11,
			                              x64.xmm12, x64.xmm13, x64.xmm14, x64.xmm15]
			self.argument_registers = [x64.rcx, x64.rdx, x64.r8, x64.r9,
			                           x64.xmm0, x64.xmm1, x64.xmm2, x64.xmm3]
			self.volatile_registers = [x64.rax, x64.r10, x64.r11,
			                           x64.mm0, x64.mm1, x64.mm2, x64.mm3, x64.mm4, x64.mm5, x64.mm6, x64.mm7,
			                           x64.xmm4, x64.xmm5]
		elif abi == 'arm-softeabi':
			self.name = 'arm-softeabi'
			self.pointer_size = 4
			self.general_purpose_register_size = 4
			self.int_size = 4
			self.long_size = 4
			self.long_long_size = 8
			self.stack_alignment = 8
			self.soft_float = True
			self.function_prefix = ""
			self.callee_save_registers = [arm.r4, arm.r5, arm.r6, arm.r7, arm.r8, arm.r9, arm.r10, arm.r11,
			                              arm.d8, arm.d9, arm.d10, arm.d11, arm.d12, arm.d13, arm.d14, arm.d15]
			self.argument_registers = [arm.r0, arm.r1, arm.r2, arm.r3]
			self.volatile_registers = [arm.r12, arm.d0, arm.d1, arm.d2, arm.d3, arm.d4, arm.d5, arm.d6, arm.d7,
			                           arm.d16, arm.d17, arm.d18, arm.d19, arm.d20, arm.d21, arm.d22, arm.d23,
			                           arm.d24, arm.d25, arm.d26, arm.d27, arm.d28, arm.d29, arm.d30, arm.d31]
		elif abi == 'arm-hardeabi':
			self.name = 'arm-hardeabi'
			self.pointer_size = 4
			self.general_purpose_register_size = 4
			self.int_size = 4
			self.long_size = 4
			self.long_long_size = 8
			self.stack_alignment = 8
			self.soft_float = False
			self.function_prefix = ""
			self.callee_save_registers = [arm.r4, arm.r5, arm.r6, arm.r7, arm.r8, arm.r9, arm.r10, arm.r11,
			                              arm.d8, arm.d9, arm.d10, arm.d11, arm.d12, arm.d13, arm.d14, arm.d15]
			self.argument_registers = [arm.r0, arm.r1, arm.r2, arm.r3]
			self.volatile_registers = [arm.r12, arm.d0, arm.d1, arm.d2, arm.d3, arm.d4, arm.d5, arm.d6, arm.d7,
			                           arm.d16, arm.d17, arm.d18, arm.d19, arm.d20, arm.d21, arm.d22, arm.d23,
			                           arm.d24, arm.d25, arm.d26, arm.d27, arm.d28, arm.d29, arm.d30, arm.d31]
		elif abi == 'mips-o32':
			self.name = 'mips-o32f'
			self.pointer_size = 4
			self.general_purpose_register_size = 4
			self.int_size = 4
			self.long_size = 4
			self.long_long_size = 8
			self.stack_alignment = 8
			self.soft_float = False
			self.function_prefix = ""

	def __str__(self):
		return self.name

	def __eq__(self, other):
		if isinstance(other, ABI):
			return self.name == other.name
		else:
			return False

	def __hash__(self):
		return hash(self.name)

	def get_name(self):
		return self.name

class Type(object):
	unsigned_integer_types = ['uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
							  'Yep8u', 'Yep16u', 'Yep32u', 'Yep64u', 'Yep128u',
							  'size_t', 'YepSize']
	signed_integer_types = ['int8_t', 'int16_t', 'int32_t', 'int64_t',
							'Yep8s', 'Yep16s', 'Yep32s', 'Yep64s', 'Yep128s',
							'jbyte', 'jshort', 'jint', 'jlong',
							'ptrdiff_t', 'ssize_t']
	integer_types = unsigned_integer_types + signed_integer_types
	floating_point_types = ['half', 'float', 'double',
							'Yep16f', 'Yep32f', 'Yep64f',
							'Yep16fc', 'Yep32fc', 'Yep64fc',
							'Yep32df', 'Yep64df',
							'Yep32dfc', 'Yep64dfc',
							'jfloat', 'jdouble']
	jni_array_types = ['jbyteArray', 'jshortArray', 'jintArray', 'jlongArray', 'jfloatArray', 'jdoubleArray']

	def __init__(self, type):
		super(Type, self).__init__()
		const_matcher = re.match("const\\s+", type)
		self.is_const_type = bool(const_matcher)
		if const_matcher:
			type = type[const_matcher.end():]
		type_matcher = re.match("[A-Za-z_][A-Za-z0-9_]*", type)
		if type_matcher:
			self.primitive_type = type_matcher.group(0)
			if self.primitive_type in Type.integer_types or self.primitive_type in Type.floating_point_types:
				type = type[type_matcher.end():]
				if type == "*":
					self.is_pointer_type = True
				elif not type:
					self.is_pointer_type = False
				else:
					raise ValueError("Unsupported primitive type suffix {0}".format(type))
			elif type in Type.jni_array_types:
				self.is_pointer_type = True
			else:
				raise ValueError("Unsupported primitive type {0}".format(self.primitive_type))
		else:
			raise ValueError("The type {0} is not recognized as a C type".format(type))

	def __eq__(self, other):
		return self.is_const_type == other.is_const_type and self.is_pointer_type == other.is_pointer_type and self.primitive_type == other.primitive_type

	def __hash__(self):
		return hash((self.is_const_type, self.is_pointer_type, self.primitive_type))

	def __str__(self):
		return self.format()

	def format(self, restrict_qualifier = "", compact_pointers = True):
		text = self.primitive_type
		if self.is_const_type:
			text = "const " + text
		if self.is_pointer_type and not self.primitive_type in Type.jni_array_types:
			if not compact_pointers:
				text += " "
			text += "*" + restrict_qualifier
		return text

	def is_size(self):
		if self.is_pointer():
			return False
		else:
			return self.primitive_type == 'size_t' or self.primitive_type == 'ssize_t' or self.primitive_type == 'YepSize'

	def is_unsigned_integer(self):
		if self.is_pointer():
			return False
		else:
			return self.primitive_type in Type.unsigned_integer_types

	def is_signed_integer(self):
		if self.is_pointer():
			return False
		else:
			return self.primitive_type in Type.signed_integer_types

	def is_integer(self):
		if self.is_pointer():
			return False
		else:
			return self.primitive_type in Type.integer_types

	def is_pointer(self):
		return self.is_pointer_type

	def is_floating_point(self):
		if self.is_pointer():
			return False
		else:
			return self.primitive_type in Type.floating_point_types

	def is_constant(self):
		return self.is_const_type

	def get_primitive_type(self):
		return Type(self.primitive_type)

	def get_size(self, abi = None):
		if self.is_pointer() or self.primitive_type in ['size_t', 'ssize_t', 'ptrdiff_t', 'YepSize']:
			if isinstance(abi, ABI):
				return abi.pointer_size
			else:
				raise TypeError('Wrong type of ABI object')
		elif self.primitive_type in ['uint8_t', 'int8_t', 'Yep8u', 'Yep8s', 'jbyte']:
			return 1
		elif self.primitive_type in ['uint16_t', 'int16_t', 'half', 'Yep16u', 'Yep16s', 'jshort']:
			return 2
		elif self.primitive_type in ['uint32_t', 'int32_t', 'float', 'Yep32u', 'Yep32s', 'Yep32f', 'jint', 'jfloat']:
			return 4
		elif self.primitive_type in ['uint64_t', 'int64_t', 'double', 'Yep64u', 'Yep64s', 'Yep64f', 'jlong', 'jdouble']:
			return 8
		else:
			raise ValueError('Unknown type {0}'.format(self.primitive_type))

	def get_std_analog(self):
		import copy
		std_type = copy.deepcopy(self)
		if self.primitive_type in ['int8_t', 'Yep8s', 'jbyte']:
			std_type.primitive_type = 'int8_t'
		elif self.primitive_type in ['int16_t', 'Yep16s', 'jshort']:
			std_type.primitive_type = 'int16_t'
		elif self.primitive_type in ['int32_t', 'Yep32s', 'jint']:
			std_type.primitive_type = 'int32_t'
		elif self.primitive_type in ['int64_t', 'Yep64s', 'jlong']:
			std_type.primitive_type = 'int64_t'
		elif self.primitive_type in ['size_t', 'ptrdiff_t', 'ssize_t']:
			pass
		elif self.primitive_type in ['uint8_t', 'Yep8u']:
			std_type.primitive_type = 'uint8_t'
		elif self.primitive_type in ['uint16_t', 'Yep16u']:
			std_type.primitive_type = 'uint16_t'
		elif self.primitive_type in ['uint32_t', 'Yep32u']:
			std_type.primitive_type = 'uint32_t'
		elif self.primitive_type in ['uint64_t', 'Yep64u']:
			std_type.primitive_type = 'uint64_t'
		elif self.primitive_type in ['float', 'Yep32f', 'jfloat']:
			std_type.primitive_type = 'float'
		elif self.primitive_type in ['double', 'Yep64f', 'jdouble']:
			std_type.primitive_type = 'double'
		else:
			return None
		return std_type
		
	def get_java_analog(self, map_unsigned_to_signed = True, size_t_analog = 'int'):
		import peachpy.java
		if self.primitive_type in ['int8_t', 'Yep8s', 'jbyte']:
			java_type = 'byte'
		elif self.primitive_type in ['int16_t', 'Yep16s', 'jshort']:
			java_type = 'short'
		elif self.primitive_type in ['int32_t', 'Yep32s', 'jint']:
			java_type = 'int'
		elif self.primitive_type in ['int64_t', 'Yep64s', 'jlong']:
			java_type = 'long'
		elif self.primitive_type in ['ptrdiff_t', 'ssize_t']:
			java_type = size_t_analog  
		elif self.primitive_type in ['uint8_t', 'Yep8u'] and map_unsigned_to_signed:
			java_type = 'byte'
		elif self.primitive_type in ['uint16_t', 'Yep16u'] and map_unsigned_to_signed:
			java_type = 'short'
		elif self.primitive_type in ['uint32_t', 'Yep32u'] and map_unsigned_to_signed:
			java_type = 'int'
		elif self.primitive_type in ['uint64_t', 'Yep64u'] and map_unsigned_to_signed:
			java_type = 'long'
		elif self.primitive_type in ['size_t', 'YepSize'] and map_unsigned_to_signed:
			java_type = size_t_analog
		elif self.primitive_type in ['float', 'Yep32f', 'jfloat']:
			java_type = 'float'
		elif self.primitive_type in ['double', 'Yep64f', 'jdouble']:
			java_type = 'double'
		else:
			return None
		if self.is_pointer():
			java_type += "[]"
		return peachpy.java.Type(java_type)

	def get_fortran_iso_c_analog(self, map_unsigned_to_signed = True, ):
		import peachpy.fortran
		if self.primitive_type in ['int8_t', 'Yep8s', 'jbyte']:
			fortran_type = 'INTEGER(C_INT8_T)'
		elif self.primitive_type in ['int16_t', 'Yep16s', 'jshort']:
			fortran_type = 'INTEGER(C_INT16_T)'
		elif self.primitive_type in ['int32_t', 'Yep32s', 'jint']:
			fortran_type = 'INTEGER(C_INT32_T)'
		elif self.primitive_type in ['int64_t', 'Yep64s', 'jlong']:
			fortran_type = 'INTEGER(C_INT64_T)'
		elif self.primitive_type in ['ptrdiff_t', 'ssize_t']:
			fortran_type = 'INTEGER(C_SIZE_T)'
		elif self.primitive_type in ['uint8_t', 'Yep8u'] and map_unsigned_to_signed:
			fortran_type = 'INTEGER(C_INT8_T)'
		elif self.primitive_type in ['uint16_t', 'Yep16u'] and map_unsigned_to_signed:
			fortran_type = 'INTEGER(C_INT16_T)'
		elif self.primitive_type in ['uint32_t', 'Yep32u'] and map_unsigned_to_signed:
			fortran_type = 'INTEGER(C_INT32_T)'
		elif self.primitive_type in ['uint64_t', 'Yep64u'] and map_unsigned_to_signed:
			fortran_type = 'INTEGER(C_INT64_T)'
		elif self.primitive_type in ['size_t', 'YepSize'] and map_unsigned_to_signed:
			fortran_type = 'INTEGER(C_SIZE_T)'
		elif self.primitive_type in ['float', 'Yep32f', 'jfloat']:
			fortran_type = 'REAL(C_FLOAT)'
		elif self.primitive_type in ['double', 'Yep64f', 'jdouble']:
			fortran_type = 'REAL(C_DOUBLE)'
		else:
			return None
		if self.is_pointer():
			fortran_type += ", DIMENSION(*)"
		return peachpy.fortran.Type(fortran_type)

	def get_csharp_analog(self, use_unsafe_types = False, size_t_analog = "System.UIntPtr", ssize_t_analog = "System.IntPtr"):
		import peachpy.csharp
		if self.primitive_type in ['int8_t', 'Yep8s', 'jbyte']:
			csharp_type = 'sbyte'
		elif self.primitive_type in ['int16_t', 'Yep16s', 'jshort']:
			csharp_type = 'short'
		elif self.primitive_type in ['int32_t', 'Yep32s', 'jint']:
			csharp_type = 'int'
		elif self.primitive_type in ['int64_t', 'Yep64s', 'jlong']:
			csharp_type = 'long'
		elif self.primitive_type in ['ptrdiff_t', 'ssize_t']:
			csharp_type = ssize_t_analog
		elif self.primitive_type in ['uint8_t', 'Yep8u']:
			csharp_type = 'byte'
		elif self.primitive_type in ['uint16_t', 'Yep16u']:
			csharp_type = 'ushort'
		elif self.primitive_type in ['uint32_t', 'Yep32u']:
			csharp_type = 'uint'
		elif self.primitive_type in ['uint64_t', 'Yep64u']:
			csharp_type = 'ulong'
		elif self.primitive_type in ['size_t', 'YepSize']:
			csharp_type = size_t_analog
		elif self.primitive_type in ['float', 'Yep32f', 'jfloat']:
			csharp_type = 'float'
		elif self.primitive_type in ['double', 'Yep64f', 'jdouble']:
			csharp_type = 'double'
		else:
			return None
		if self.is_pointer():
			if use_unsafe_types:
				csharp_type += "*"
			else:
				csharp_type += "[]"
		return peachpy.csharp.Type(csharp_type)

class Parameter(object):
	def __init__(self, name, ctype):
		super(Parameter, self).__init__()
		if isinstance(name, str):
			self.name = name
		else:
			raise TypeError('Parameter name must be a string')
		if isinstance(ctype, Type):
			self.type = ctype
		else:
			raise TypeError('Parameter type must be an instance of Type object')

	def __eq__(self, other):
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)

	def __str__(self):
		return self.format()

	def format(self, restrict_qualifier = "", compact_pointers = True):
		return self.get_type().format(restrict_qualifier, compact_pointers) + " " + self.get_name()

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def get_size(self, abi):
		return self.type.get_size(abi)
