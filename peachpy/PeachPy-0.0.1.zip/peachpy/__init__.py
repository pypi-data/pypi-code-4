#
#        PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

__version_info__ = ('0', '0', '1')
__version__ = '.'.join(__version_info__)

class ConstantBucket(object):
	supported_capacity = [1, 2, 4, 8, 16, 32, 64, 128]

	def __init__(self, capacity):
		super(ConstantBucket, self).__init__()
		if isinstance(capacity, int):
			if capacity in ConstantBucket.supported_capacity:
				self.capacity = capacity
			else:
				raise ValueError("Capacity value {0} is not among the supports capacities ({1})".format(capacity, ConstantBucket.supported_capacity))
		else:
			raise TypeError("Constant capacity {0} must be an integer".format(capacity))
		self.size = 0
		self.constants = list()

	def add(self, constant):
		if isinstance(constant, Constant):
			if constant.get_alignment() > self.get_capacity() * 8:
				raise ValueError("Constants alignment exceeds constant bucket alignment")
			elif (self.size * 8) % constant.get_alignment() != 0:
				raise ValueError("Constant alignment is not compatible with the internal constant bucket alignment")
			elif self.size + constant.size * constant.repeats / 8 > self.capacity:
				raise ValueError("Constant bucket is overflowed")
			else:
				self.constants.append(constant)
				self.size += constant.size * constant.repeats / 8
		else:
			raise TypeError("Only Constant objects can be added to a constant bucket")

	def get_capacity(self):
		return self.capacity

	def is_empty(self):
		return self.size == 0

	def is_full(self):
		return self.size == self.capacity

	def empty(self):
		constants = self.constants
		self.constants = list()
		return constants

class Constant(object):
	supported_sizes = [8, 16, 32, 64, 128, 256]
	supported_types = ['uint8', 'uint16', 'uint32', 'uint64', 'uint128', 'uint256',
	                   'sint8', 'sint16', 'sint32', 'sint64', 'sint128', 'sint256',
	                   'int8',  'int16',  'int32',  'int64',  'int128',  'int256',
	                   'float16', 'float32', 'float64', 'float80', 'float128']

	def __init__(self, size, repeats, data, basic_type):
		super(Constant, self).__init__()
		if isinstance(size, int):
			if size in Constant.supported_sizes:
				self.size = size
			else:
				raise ValueError("Constant size {0} is not among the supported sizes ({1})".format(size, ", ".join(Constant.supported_sizes)))
		else:
			raise TypeError("Constant size {0} must be an integer".format(size))
		if isinstance(repeats, int):
			if size in Constant.supported_sizes:
				self.repeats = repeats
			else:
				raise ValueError("The number of constant repeats {0} is not among the supported repeat numbers ({1})".format(repeats, ", ".join(Constant.supported_sizes)))
		else:
			raise TypeError("The number of constant repeats {0} must be an integer".format(repeats))
		if isinstance(basic_type, str):
			if basic_type in Constant.supported_types:
				self.basic_type = basic_type
		else:
			raise TypeError("The basic type {0} of a constant must be an integer".format(basic_type))
		self.data = data
		self.label = None
		self.prefix = None

	def __str__(self):
		text = hex(self.data)
		if text.endswith("L"):
			text = text[:-1]
		if text.startswith("0x"):
			text = text[2:]
		if len(text) < self.size * 2:
			text = "0" * (self.size / 4 - len(text)) + text
		text = "0x" + text.upper()
		if self.size == 8:
			return text
		elif self.size == 16:
			return text
		elif self.size == 32:
			return text
		elif self.size == 64:
			return text
		elif self.size == 128:
			return text

	def __hash__(self):
		return hash(self.data) ^ hash(self.size) ^ hash(self.repeats)

	def __eq__(self, other):
		if isinstance(other, Constant):
			if self.size == other.size and self.repeats == other.repeats:
				return self.data == other.data
			else:
				return False
		else:
			return False

	def get_alignment(self):
		if self.size == 80:
			return 128
		else:
			return self.size * self.repeats

	@staticmethod
	def is_int64(number):
		if isinstance(number, int) or isinstance(number, long):
			return -9223372036854775808L <= number <= 18446744073709551615L
		else:
			return False

	@staticmethod
	def as_uint64(number):
		assert Constant.is_int64(number)
		if 0 <= number <= 18446744073709551615L:
			return long(number)
		else:
			return long(number + 18446744073709551616L)

	@staticmethod
	def is_int32(number):
		if isinstance(number, int) or isinstance(number, long):
			return -2147483648L <= number <= 4294967295L
		else:
			return False

	@staticmethod
	def as_uint32(number):
		assert Constant.is_int32(number)
		if 0 <= number <= 4294967295L:
			return long(number)
		else:
			return long(number + 4294967296L)

	@staticmethod
	def uint64(number):
		if isinstance(number, int) or isinstance(number, long):
			if Constant.is_int64(number):
				return Constant(64, 1, Constant.as_uint64(number + 18446744073709551616L))
			else:
				raise ValueError("The number {0} is not a 64-bit integer".format(number))
		else:
			raise TypeError("The number used to construct a 64-bit unsigned integer constant must be an integer")

	@staticmethod
	def uint64x2(number1, number2 = None):
		if Constant.is_int64(number1):
			number1 = Constant.as_uint64(number1)
		else:
			raise ValueError("The number {0} is not a 64-bit integer".format(number1))
		if number2 is None:
			number2 = number1
		elif Constant.is_int64(number2):
			number2 = Constant.as_uint64(number2)
		else:
			raise ValueError("The number {0} is not a 64-bit integer".format(number2))
		if number1 == number2:
			return Constant(64, 2, number1, 'uint64')
		else:
			return Constant(128, 1, (number1 << 64) + number2, 'uint64')

	@staticmethod
	def uint64x4(number1, number2 = None, number3 = None, number4 = None):
		if isinstance(number1, int) or isinstance(number1, long):
			if Constant.is_int64(number1):
				number1 = Constant.as_uint64(number1)
			else:
				raise ValueError("The number {0} is not a 64-bit integer".format(number1))
		else:
			raise TypeError("The number used to construct a 64-bit unsigned integer constant must be an integer")
		if number2 is None or number3 is None or number4 is None:
			if number2 is None and number3 is None and number4 is None:
				number2 = number1
				number3 = number1
				number4 = number1
			else:
				raise ValueError("Either one or four values must be supplied")
		elif Constant.is_int64(number2) and Constant.is_int64(number3) and Constant.is_int64(number4):
			number2 = Constant.as_uint64(number2)
			number3 = Constant.as_uint64(number3)
			number4 = Constant.as_uint64(number4)
		else:
			raise ValueError("The one of the numbers ({0}, {1}, {2}) is not a 64-bit integer".format(number2, number3, number4))
		if number1 == number2 == number3 == number4:
			return Constant(64, 4, number1, 'uint64')
		elif number1 == number3 and number2 == number4:
			return Constant(128, 2, (number1 << 64) + number2, 'uint64')
		else:
			return Constant(256, 1, (number1 << 192) + (number2 << 128) + (number3 << 64) + number4, 'uint64')
	
	@staticmethod
	def uint32x4(number1, number2 = None, number3 = None, number4 = None):
		if isinstance(number1, int) or isinstance(number1, long):
			if Constant.is_int32(number1):
				number1 = Constant.as_uint32(number1)
			else:
				raise ValueError("The number {0} is not a 32-bit integer".format(number1))
		else:
			raise TypeError("The number used to construct a 32-bit unsigned integer constant must be an integer")
		if number2 is None or number3 is None or number4 is None:
			if number2 is None and number3 is None and number4 is None:
				number2 = number1
				number3 = number1
				number4 = number1
			else:
				raise ValueError("Either one or four values must be supplied")
		elif Constant.is_int32(number2) and Constant.is_int32(number3) and Constant.is_int32(number4):
			number2 = Constant.as_uint32(number2)
			number3 = Constant.as_uint32(number3)
			number4 = Constant.as_uint32(number4)
		else:
			raise ValueError("The one of the numbers ({0}, {1}, {2}) is not a 32-bit integer".format(number2, number3, number4))
		if number1 == number2 == number3 == number4:
			return Constant(32, 4, number1, 'uint32')
		elif number1 == number3 and number2 == number4:
			return Constant(64, 2, (number1 << 32) + number2, 'uint32')
		else:
			return Constant(128, 1, (number1 << 96) + (number2 << 64) + (number3 << 32) + number4, 'uint32')

	@staticmethod
	def uint32x8(number1, number2 = None, number3 = None, number4 = None, number5 = None, number6 = None, number7 = None, number8 = None):
		if isinstance(number1, int) or isinstance(number1, long):
			if Constant.is_int32(number1):
				number1 = Constant.as_uint32(number1)
			else:
				raise ValueError("The number {0} is not a 32-bit integer".format(number1))
		else:
			raise TypeError("The number used to construct a 32-bit unsigned integer constant must be an integer")
		numbers = [number2, number3, number4, number5, number6, number7, number8]
		if any(number is None for number in numbers):
			if all(number is None for number in numbers):
				number2 = number1
				number3 = number1
				number4 = number1
				number5 = number1
				number6 = number1
				number7 = number1
				number8 = number1
			else:
				raise ValueError("Either one or eight values must be supplied")
		elif all(Constant.is_uint32(number) for number in numbers):
			number2 = Constant.as_uint32(number2)
			number3 = Constant.as_uint32(number3)
			number4 = Constant.as_uint32(number4)
			number5 = Constant.as_uint32(number5)
			number6 = Constant.as_uint32(number6)
			number7 = Constant.as_uint32(number7)
			number8 = Constant.as_uint32(number8)
		else:
			raise ValueError("The one of the numbers ({0}, {1}, {2}) is not a 32-bit integer".format(number2, number3, number4))
		if number1 == number2 == number3 == number4 == number5 == number6 == number7 == number8:
			return Constant(32, 8, number1, 'uint32')
		elif number1 == number3 == number5 == number7 and number2 == number4 == number6 == number8:
			return Constant(64, 4, (number1 << 32) + number2, 'uint32')
		elif number1 == number5 and number2 == number6 and number3 == number7 and number4 == number8:
			return Constant(128, 2, (number1 << 96) + (number2 << 64) + (number3 << 32) + number4, 'uint32')
		else:
			return Constant(256, 1, (number1 << 224) + (number2 << 192) + (number3 << 160) + (number4 << 128) + (number5 << 96) + (number6 << 64) + (number7 << 32) + number8, 'uint32')

	@staticmethod
	def uint32(number):
		if isinstance(number, int) or isinstance(number, long):
			if 0 <= number <= 4294967295L:
				return Constant(32, 1, long(number), 'uint32')
			elif -2147483648L <= number < 0:
				return Constant(32, 1, long(number + 4294967296L), 'uint32')
			else:
				raise ValueError("The number {0} is not a 32-bit integer".format(number))
		else:
			raise TypeError("The number used to construct a 32-bit unsigned integer constant must be an integer")

	@staticmethod
	def uint16(number):
		if isinstance(number, int) or isinstance(number, long):
			if 0 <= number <= 65535:
				return Constant(16, 1, long(number), 'uint16')
			elif -32768 <= number < 0:
				return Constant(16, 1, long(number + 65536), 'uint16')
			else:
				raise ValueError("The number {0} is not a 16-bit integer".format(number))
		else:
			raise TypeError("The number used to construct a 16-bit unsigned integer constant must be an integer")

	@staticmethod
	def uint8(number):
		if isinstance(number, int) or isinstance(number, long):
			if 0 <= number <= 255:
				return Constant(8, 1, long(number), 'uint8')
			elif -128 <= number < 0:
				return Constant(8, 1, long(number + 256), 'uint8')
			else:
				raise ValueError("The number {0} is not an 8-bit integer".format(number))
		else:
			raise TypeError("The number used to construct an 8-bit unsigned integer constant must be an integer")

	@staticmethod
	def float64(number):
		return Constant(64, 1, Constant.parse_float64(number), 'float64')

	@staticmethod
	def float64x2(number1, number2 = None):
		number1 = Constant.parse_float64(number1)
		if number2 is None:
			number2 = number1
		else:
			number2 = Constant.parse_float64(number2)
		if number1 == number2:
			return Constant(64, 2, number1, 'float64')
		else:
			return Constant(128, 1, (number1 << 64) + number2, 'float64')

	@staticmethod
	def float64x4(number1, number2 = None, number3 = None, number4 = None):
		number1 = Constant.parse_float64(number1)
		if number2 is None or number3 is None or number4 is None:
			if number3 is None and number4 is None:
				number2 = number1
				number3 = number1
				number4 = number1
			else:
				raise ValueError("Either one or four values must be supplied")
		else:
			number2 = Constant.parse_float64(number2)
			number3 = Constant.parse_float64(number3)
			number4 = Constant.parse_float64(number4)
		if number1 == number2 == number3 == number4:
			return Constant(64, 4, number1, 'float64')
		elif number1 == number3 and number2 == number4:
			return Constant(128, 2, (number1 << 64) + number2, 'float64')
		else:
			return Constant(256, 1, (number1 << 192) + (number2 << 128) + (number3 << 64) + number4, 'float64')

	@staticmethod
	def parse_float64(number):
		if isinstance(number, float):
			number = float.hex(number)
		elif isinstance(number, str):
			if number == "inf" or number == "+inf":
				return 0x7FF0000000000000L
			elif number == "-inf":
				return 0xFFF0000000000000L
			elif number == "nan":
				return 0x7FF8000000000000L
			else:
				# Validity check
				float.hex(float.fromhex(number))
		else:
			raise TypeError('Unsupported constant type {0} for constant {1}'.format(type(number), number))
		is_negative = number.startswith("-")
		point_position = number.index('.')
		exp_position = number.rindex('p')
		number_prefix = number[int(is_negative):point_position]
		assert number_prefix == '0x0' or number_prefix == '0x1'
		mantissa = number[point_position + 1:exp_position]
		if number_prefix == '0x0' and int(mantissa) == 0:
			# Zero
			return long(is_negative) << 63
		else:
			exponent = number[exp_position + 1:]
			mantissa_bits = len(mantissa) * 4
			if mantissa_bits == 52:
				mantissa = long(mantissa, 16)
			elif mantissa_bits < 52:
				mantissa = long(mantissa, 16) << (52 - mantissa_bits)
			else:
				mantissa = long(mantissa, 16) >> (mantissa_bits - 52)
			exponent = int(exponent)
			if exponent <= -1023:
				# Denormals
				mantissa = (mantissa + (1 << 52) ) >> -(exponent + 1022)
				exponent = -1023
			elif exponent > 1023:
				# Infinity
				mantissa = 0
				exponent = 1023
			return mantissa + (long(exponent + 1023) << 52) + (long(is_negative) << 63)

class RegisterAllocationError(Exception):
	pass