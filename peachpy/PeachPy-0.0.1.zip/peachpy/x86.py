#
#        PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

import peachpy.c
import peachpy.codegen

__author__ = 'Marat'

current_function = None
supported_isa_extensions = ['CMOV', 'MMX', 'MMX+', '3dnow!', '3dnow!+', '3dnow! Prefetch', '3dnow! Geode',
							'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2',
							'AVX', 'AVX2', 'FMA3', 'FMA4', 'F16C',
							'MOVBE', 'POPCNT', 'LZCNT', 'TZCNT', 'BMI', 'BMI2', 'TBM',
							'AES']

class Microarchitecture(object):
	supported_microarchitectures = ['P5', 'P6', 'Willamette', 'Prescott', 'Dothan', 'Yonah', 'Conroe', 'Penryn', 'Bonnell',
	                                'Nehalem', 'SandyBridge', 'Saltwell', 'IvyBridge', 'Haswell', 'KnightsFerry', 'KnightsCorner',
	                                'K5', 'K6', 'K7', 'Geode', 'K8', 'K10', 'Bobcat', 'Bulldozer', 'Piledriver', 'Jaguar', 'Steamroller']

	abbreviations = {'P5': 'P5', 'P6': 'P6', 'Willamette': 'P4W', 'Prescott': 'P4P', 'Dothan': 'DTH', 'Yonah': 'YNH',
	                    'Conroe': 'CNR', 'Penryn': 'PNR', 'Bonnell': 'BNL', 'Nehalem': 'NHM', 'SandyBridge': 'SNB',
	                    'Salwell': 'SLW', 'IvyBridge': 'IVB', 'Haswell': 'HSW',' KnightsFerry': 'KNF', 'KnightsCorner': 'KNC',
	                    'K5': 'K5', 'K6': 'K6', 'K7': 'K7', 'Geode': 'GDE', 'K8': 'K8', 'K10': 'K10', 'Bobcat': 'BCT',
	                    'Bulldozer': 'BLD', 'Piledriver': 'PLD', 'Jaguar': 'JAG', 'Steamroller': 'STR'}

	def __init__(self, name):
		super(Microarchitecture, self).__init__()
		if name in Microarchitecture.supported_microarchitectures:
			self.name = name
		else:
			raise ValueError('Unsupported microarchitecture {0}: only ({1}) microarchitectures are supported on this architecture'.format(name, ', '.join(Microarchitecture.supported_microarchitectures)))

	def get_name(self):
		return self.name

	def get_number(self):
		return Microarchitecture.supported_microarchitectures.index(self.get_name())

	def get_yeppp_name(self):
		return "YepCpuMicroarchitecture" + self.name

class Assembler(peachpy.codegen.CodeGenerator):
	def __init__(self, abi):
		super(Assembler, self).__init__()
		if isinstance(abi, peachpy.c.ABI):
			if abi.get_name() == 'x86':
				self.abi = abi
			else:
				raise ValueError('Unsupported abi {0}: only "x64-ms", "x64-sysv" and "x32" ABIs are supported on this architecture'.format(abi))
		else:
			raise TypeError('Wrong type of ABI object')
		self.functions = list()

	def begin_function(self, name, arguments, microarchitecture):
		global current_function
		if current_function is not None:
			raise ValueError('Function {0} was not finalized'.format(current_function.name))
		current_function = Function(name, arguments, Microarchitecture(microarchitecture), self.abi)

	def end_function(self):
		global current_function
		if current_function is None:
			raise ValueError('Trying to finalize a function while no function is active')
		current_function.generate_prolog_and_epilog()
		current_function.generate_entry_label()
		current_function.determine_available_registers()
		current_function.determine_live_registers()
		current_function.determine_stack_offsets()
		current_function.generate_parameter_loads()
		current_function.generate_constant_loads()
		self.functions.append(current_function)
		function = current_function
		current_function = None

		instructions = function.instructions
		constants = function.constants

		function_label = "_" + function.symbol_name
		constants_label = function.symbol_name + "_constants"
		if len(constants) > 0:
			self.add_line('section .data.{0} progbits alloc noexec write align={1}'.format(function.microarchitecture.get_number(), function.constant_max_alignment))
			self.add_line(constants_label + ':')
			data_declaration_map = {8: "DB", 16: "DW", 32: "DD", 64: "DQ", 128: "DO"}
			self.indent()
			for constant in constants:
				self.add_line(".{0} {1} {2}".format(constant.label, data_declaration_map[constant.size], ", ".join([str(constant)] * constant.repeats)))
				constant.label = constants_label + "." + constant.label
			for (alignment, constant_bucket) in function.constant_buckets.iteritems():
				if not constant_bucket.is_empty():
					self.add_line("align {0}".format(alignment))
					for constant in constant_bucket.empty():
						self.add_line(".{0} {1} {2}".format(constant.label, data_declaration_map[constant.size], ", ".join([str(constant)] * constant.repeats)))
			self.dedent()
			self.add_line()
			self.add_line()

		self.add_line('section .text.{0} progbits alloc exec nowrite align=16'.format(function.microarchitecture.get_number()))
		self.add_line("global " + function_label)
		self.add_line(function_label + ':')
		self.indent()
		for instruction in instructions:
			if isinstance(instruction, Instruction):
				consumed_registers = ", ".join(sorted(map(str, list(instruction.get_input_registers_list()))))
				produced_registers = ", ".join(sorted(map(str, list(instruction.get_output_registers_list()))))
				available_registers = ", ".join(sorted(map(str, list(instruction.available_registers))))
				live_registers = ", ".join(sorted(map(str, list(instruction.live_registers))))
				if len(instruction) > 1:
					self.add_line("{0:50s} ; {1:<2d} bytes | {2:12s} | {3:12s} | {4}".format(instruction, len(instruction), consumed_registers, produced_registers, live_registers))
				else:
					self.add_line("{0:50s} ; 1  byte  | {1:12s} | {2:12s} | {3}".format(instruction, consumed_registers, produced_registers, live_registers))
			elif isinstance(instruction, Label):
				self.add_line(str(instruction), indent = 0)
			else:
				self.add_line(str(instruction))
		self.dedent()
		self.add_line()
		return function

	def __str__(self):
		return self.get_code()

class Function(object):
	def __init__(self, name, arguments, microarchitecture, abi):
		super(Function, self).__init__()
		self.name = name
		self.arguments = arguments
		self.microarchitecture = microarchitecture
		self.symbol_name = "_" + name + "_" + microarchitecture.get_name()
		self.abi = abi
		self.stack_offset = 0
		self.instructions = list()
		self.constants = list()
		self.constant_buckets = dict()
		self.constants_size = 0
		self.constant_max_alignment = 1
		self.virtual_avx_registers_count = 0
		self.virtual_sse_registers_count = 0
		self.virtual_mmx_registers_count = 0
		self.virtual_general_purpose_registers_count = 0

	def has_parameter(self, parameter):
		return parameter in self.arguments

	def get_parameter_offset(self, parameter):
		offset = 4
		for argument in self.arguments:
			if argument == parameter:
				return offset
			else:
				offset += 4
		raise ValueError("No parameter with name {0} found".format(parameter))

	def add_instruction(self, instruction):
		self.instructions.append(instruction)

	def add_constant(self, constant):
		if constant in self.constants:
			constant_index = self.constants.index(constant)
			constant.address_offset = self.constants[constant_index].address_offset
			constant.label = self.constants[constant_index].label
		else:
			constant.address_offset = self.constants_size
			constant.label = "c" + str(len(self.constants))
			self.constants_size += constant.size * constant.repeats
			self.constants.append(constant)
		assert constant.address_offset % (constant.size * constant.repeats) == 0

	def get_modified_registers_set(self, instructions):
		modified_registers = set()
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				for output_register in instruction.get_output_registers_list():
					modified_registers.add(output_register)
		return modified_registers

	def generate_prolog_and_epilog(self):
		nonvolatile_registers = set(self.abi.callee_save_registers)
		modified_registers = self.get_modified_registers_set(self.instructions)
		onstack_registers = list(nonvolatile_registers.intersection(modified_registers))
		push_instructions = [PushInstruction(Operand(register)) for register in onstack_registers]
		pop_instructions = [PopInstruction(Operand(register)) for register in reversed(onstack_registers)]
		new_instructions = push_instructions
		for instruction in self.instructions:
			if isinstance(instruction, ReturnInstruction):
				new_instructions.extend(pop_instructions)
				new_instructions.extend(instruction.to_instruction_list())
			elif isinstance(instruction, RetInstruction):
				new_instructions.extend(pop_instructions)
				new_instructions.append(instruction)
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions

	def generate_entry_label(self):
		for instruction in self.instructions:
			if isinstance(instruction, Label):
				if instruction.name == 'ENTRY':
					return
		self.instructions.insert(0, Label("ENTRY"))

	def generate_else_labels(self):
		follows_branch_instruction = False
		label_number = 0
		new_instructions = list()
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, ConditionalJumpInstruction):
				follows_branch_instruction = True
			else:
				if not isinstance(instruction, Label) and follows_branch_instruction:
					new_instructions.append(Label("L" + str(label_number)))
					label_number += 1
				follows_branch_instruction = False
			new_instructions.append(instruction)
		self.instructions = new_instructions

	def get_label_table(self):
		label_table = dict()
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, Label):
				label_table[instruction.name] = index
		return label_table

	def find_entry_label(self):
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, Label):
				if instruction.name == 'ENTRY':
					return index
		raise ValueError('Instruction stream does not contain the ENTRY label')

	def find_ret_instructions(self):
		ret_instructions = list()
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, RetInstruction):
				ret_instructions.append(index)
		return ret_instructions

	def determine_available_registers(self):
		def mark_available_registers(instructions, start, initial_available_registers, label_table):
			available_registers = set(initial_available_registers)
			for i in range(start, len(instructions)):
				instruction = instructions[i]
				if isinstance(instruction, Instruction):
					instruction.available_registers = set(available_registers)
					if isinstance(instruction, ConditionalJumpInstruction):
						target_label = instruction.destination
						target_index = label_table[target_label]
						if not i in instructions[target_index].input_branches:
							instructions[target_index].input_branches.add(i)
							mark_available_registers(instructions, target_index, available_registers, label_table)
					elif isinstance(instruction, JmpInstruction):
						target_label = instruction.destination
						target_index = label_table[target_label]
						if not i in instructions[target_index].input_branches:
							instructions[target_index].input_branches.add(i)
							mark_available_registers(instructions, target_index, available_registers, label_table)
						return
					else:
						available_registers |= set(instruction.get_output_registers_list())

		label_table = self.get_label_table()
		current_index = self.find_entry_label()
		mark_available_registers(self.instructions, current_index, set(), label_table)

	def determine_live_registers(self):
		def mark_live_registers(instructions, end, initial_live_registers):
			live_registers = set(initial_live_registers)
			for i in range(end, -1, -1):
				instruction = instructions[i]
				if isinstance(instruction, JmpInstruction) and i != end:
					return
				elif isinstance(instruction, Instruction):
#					live_registers -= set(instruction.get_output_registers_list())
					new_live_registers = list()
					for live_register in live_registers:
						unmodified_write_register = True
						for output_register in instruction.get_output_registers_list():
							if live_register in output_register:
								unmodified_write_register = False
								break
						if unmodified_write_register:
							new_live_registers.append(live_register)
					live_registers = set(new_live_registers)

					live_registers |= set(instruction.get_input_registers_list())
#					instruction.live_registers = set(instruction.live_registers | live_registers)
					instruction.live_registers = Register.eliminate_enclosed_registers(set(instruction.live_registers | live_registers))
				elif isinstance(instruction, Label):
					for target_index in instruction.input_branches:
						if not instructions[target_index].is_visited:
							instructions[target_index].is_visited = True
							mark_live_registers(instructions, target_index, live_registers)

		ret_instructions = self.find_ret_instructions()
		for ret_instruction in ret_instructions:
			mark_live_registers(self.instructions, ret_instruction, set())

	def determine_stack_offsets(self):
		stack_offset = 0
		for instruction in self.instructions:
			setattr(instruction, 'stack_offset', stack_offset)
			if isinstance(instruction, PushInstruction):
				stack_offset += 4
			elif isinstance(instruction, PopInstruction):
				stack_offset -= 4
			elif isinstance(instruction, RetInstruction):
				pass
			elif isinstance(instruction, Instruction):
				if esp in instruction.get_output_registers_list():
					raise TypeError('Instruction {0} changes stack pointer in unsupported way'.format(instruction))

		# Check labels
		label_table = self.get_label_table()
		for instruction in self.instructions:
			if isinstance(instruction, ConditionalJumpInstruction) or isinstance(instruction, JmpInstruction):
				branch_target = instruction.destination
				if self.instructions[label_table[branch_target]].stack_offset != instruction.stack_offset:
					raise ValueError('Stack offset for label {0} is different than for branch instruction {1}'.format(branch_target, instruction))

	def generate_parameter_loads(self):
		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, LoadParameterPseudoInstruction):
				parameter_name = instruction.parameter
				parameter_offset = instruction.stack_offset + self.get_parameter_offset(parameter_name)
				new_instructions.append(MovInstruction(instruction.destination, Operand([esp + parameter_offset])))
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions

	def generate_constant_loads(self):
		max_alignment = 1
		for constant in self.constants:
			max_alignment = max(max_alignment, constant.get_alignment() / 8)
		self.constant_max_alignment = max_alignment

		alignment = 1
		while alignment < max_alignment:
			self.constant_buckets[alignment] = ConstantBucket(max_alignment)
			alignment *= 2

		new_constants = list()
		for constant in self.constants:
			if constant.get_alignment() == max_alignment * 8:
				new_constants.append(constant)
			else:
				constant_bucket = self.constant_buckets[constant.get_alignment() / 8]
				constant_bucket.add(constant)
				if constant_bucket.is_full():
					new_constants.append(constant_bucket.empty())
		self.constants = new_constants

		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, LoadConstantPseudoInstruction):
				constant = instruction.source.constant
				if constant.size * constant.repeats == 128:
					if constant.basic_type == 'float32':
						new_instructions.append(SseMovInstruction('MOVAPS', instruction.destination, instruction.source))
					elif constant.basic_type == 'float64':
						new_instructions.append(SseMovInstruction('MOVAPD', instruction.destination, instruction.source))
					else:
						new_instructions.append(SseMovInstruction('MOVDQA', instruction.destination, instruction.source))
				else:
					assert False
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions

	def get_isa_extensions(self):
		isa_extensions = set()
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				isa_extensions.add(instruction.get_isa_extension())
		return list(isa_extensions)

	def get_yeppp_isa_extensions(self):
		isa_extensions_map = {'CMOV':            ('CMOV',       None,           None),
		                      'MMX':             ( None,       'MMX',          'FPU'),
		                      'MMX+':            ( None,       'MMXPlus',      'FPU'),
		                      '3dnow!':          ( None,       '3dnow',        'FPU'),
		                      '3dnow!+':         ( None,       '3dnowPlus',    'FPU'),
		                      '3dnow! Prefetch': ( None,       '3dnowPrefetch', None),
		                      '3dnow! Geode':    ( None,       '3dnowGeode',   'FPU'),
		                      'SSE':             ( None,       'SSE',          'SSE'),
		                      'VSSE':            ( None,       'SSE',          'AVX'),
		                      'SSE2':            ( None,       'SSE2',         'SSE'),
		                      'VSSE2':           ( None,       'SSE2',         'AVX'),
		                      'SSE3':            ( None,       'SSE3',         'SSE'),
		                      'VSSE3':           ( None,       'SSE3',         'AVX'),
		                      'SSSE3':           ( None,       'SSSE3',        'SSE'),
		                      'VSSSE3':          ( None,       'SSSE3',        'AVX'),
		                      'SSE4A':           ( None,       'SSE4A',        'SSE'),
		                      'VSSE4A':          ( None,       'SSE4A',        'AVX'),
		                      'SSE4.1':          ( None,       'SSE4_1',       'SSE'),
		                      'VSSE4.1':         ( None,       'SSE4_1',       'AVX'),
		                      'SSE4.2':          ( None,       'SSE4_2',       'SSE'),
		                      'VSSE4.2':         ( None,       'SSE4_2',       'AVX'),
		                      'AVX':             ( None,       'AVX',          'AVX'),
		                      'AVX2':            ( None,       'AVX2',         'AVX'),
		                      'FMA3':            ( None,       'FMA3',         'AVX'),
		                      'FMA4':            ( None,       'FMA4',         'AVX'),
		                      'F16C':            ( None,       'F16C',         'AVX'),
							  'MOVBE':           ('Movbe',      None,           None),
							  'POPCNT':          ('Popcnt',     None,           None),
							  'LZCNT':           ('Lzcnt',      None,           None),
							  'TZCNT':           ('Tzcnt',      None,           None),
							  'BMI':             ('BMI',        None,           None),
							  'BMI2':            ('BMI2',       None,           None),
							  'TBM':             ('TBM',        None,           None),
							  'AES':             ('AES',        None,          'SSE'),
							  'VAES':            ('AES',        None,          'AVX'),
							  'RDRAND':          ('Rdrand',     None,           None),
							  'RDSEED':          ('Rdseed',     None,           None),
							  'PCLMULQDQ':       ('Pclmulqdq',  None,          'SSE'),
							  'VPCLMULQDQ':      ('Pclmulqdq',  None,          'AVX')}
		(isa_extensions, simd_extensions, system_extensions) = (list(), list(), list())
		for isa_extension in self.get_isa_extensions():
			if not isa_extension is None:
				(isa_extension, simd_extension, system_extension) = isa_extensions_map[isa_extension]
				if not isa_extension is None:
					isa_extensions.append(isa_extension)
				if not simd_extension is None:
					simd_extensions.append(simd_extension)
				if not system_extension is None:
					system_extensions.append(system_extension)
		isa_extensions = map(lambda id: "YepX86IsaFeature" + id, isa_extensions)
		if len(isa_extensions) == 0:
			isa_extensions = ["YepIsaFeaturesDefault"]
		simd_extensions = map(lambda id: "YepX86SimdFeature" + id, simd_extensions)
		if len(simd_extensions) == 0:
			simd_extensions = ["YepSimdFeaturesDefault"]
		system_extensions = map(lambda id: "YepX86SystemFeature" + id, system_extensions)
		if len(system_extensions) == 0:
			system_extensions = ["YepSystemFeaturesDefault"]
		return (isa_extensions, simd_extensions, system_extensions)

	def allocate_avx_register(self):
		self.virtual_avx_registers_count += 1
		return self.virtual_avx_registers_count

	def allocate_sse_register(self):
		self.virtual_sse_registers_count += 1
		return self.virtual_sse_registers_count

	def allocate_mmx_register(self):
		self.virtual_mmx_registers_count += 1
		return self.virtual_mmx_registers_count

	def allocate_general_purpose_register32(self):
		self.virtual_general_purpose_registers_count += 1
		return self.virtual_general_purpose_registers_count

	def allocate_general_purpose_register16(self):
		self.virtual_general_purpose_registers_count += 1
		return self.virtual_general_purpose_registers_count

	def allocate_general_purpose_register8(self):
		self.virtual_general_purpose_registers_count += 1
		return self.virtual_general_purpose_registers_count

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
		self.address_offset = None
		self.label = None
		current_function.add_constant(self)

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

	def __eq__(self, other):
		if isinstance(other, Constant):
			if self.size == other.size and self.repeats == other.repeats:
				return True
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
	def uint64(number):
		if isinstance(number, int) or isinstance(number, long):
			if 0 <= number <= 18446744073709551615L:
				return Constant(64, 1, long(number))
			elif -9223372036854775808L <= number < 0:
				return Constant(64, 1, long(number + 18446744073709551616L))
			else:
				raise ValueError("The number {0} is not a 64-bit integer".format(number))
		else:
			raise TypeError("The number used to construct a 64-bit unsigned integer constant must be an integer")

	@staticmethod
	def uint64x2(number1, number2 = None):
		if isinstance(number1, int) or isinstance(number1, long):
			if 0 <= number1 <= 18446744073709551615L:
				number1 = long(number1)
			elif -9223372036854775808L <= number1 < 0:
				number1 = long(number1 + 18446744073709551616L)
			else:
				raise ValueError("The number {0} is not a 64-bit integer".format(number1))
		else:
			raise TypeError("The number used to construct a 64-bit unsigned integer constant must be an integer")
		if number2 is None:
			number2 = number1
		elif isinstance(number2, int) or isinstance(number2, long):
			if 0 <= number2 <= 18446744073709551615L:
				number2 = long(number2)
			elif -9223372036854775808L <= number2 < 0:
				number2 = long(number2 + 18446744073709551616L)
			else:
				raise ValueError("The number {0} is not a 64-bit integer".format(number2))
		else:
			raise TypeError("The number used to construct a 64-bit unsigned integer constant must be an integer")
		if number1 == number2:
			return Constant(64, 2, number1, 'uint64')
		else:
			return Constant(128, 1, (number1 << 64) + number2, 'uint64')

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
		return Constant(64, 1, Constant.parse_float64(number), is_floating_point = True)

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
	def parse_float64(number):
		if isinstance(number, float):
			number = float.hex(number)
		elif isinstance(number, int) or isinstance(number, long):
			number = float.hex(float(number))
		elif isinstance(number, str):
			# Validity check
			float.hex(float.fromhex(number))
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

class Register(object):
	def __init__(self):
		super(Register, self).__init__()

	def __eq__(self, other):
		if isinstance(other, Register):
			if not self.is_virtual():
				if not other.is_virtual():
					return self.name == other.name
				else:
					return False
			else:
				if other.is_virtual():
					return self.number == other.number
				else:
					return False
		else:
			return False

	def __hash__(self):
		if self.is_virtual():
			return hash(self.number)
		else:
			return hash(self.name)

	def __ilshift__(self, other):
		if isinstance(other, Constant):
			current_function.add_instruction(LoadConstantPseudoInstruction(Operand(self), Operand(other)))
		else:
			raise TypeError('Loading via <<= operator is supported only for Constants')

	def __contains__(self, register):
		if self.is_virtual():
			return self.number == register.number
		else:
			return self.name == register.name

	@staticmethod
	def eliminate_enclosed_registers(registers):
		new_registers = set()
		for register in registers:
			added_register = False
			for new_register in new_registers:
				if register in new_register:
					added_register = True
					break
				elif new_register in register:
					new_registers.remove(new_register)
					new_registers.add(register)
					added_register = True
					break
			if not added_register:
				new_registers.add(register)
		return new_registers

	def is_virtual(self):
		if self.name is None:
			return True
		else:
			return False

class GeneralPurposeRegister(Register):
	def __init__(self):
		super(GeneralPurposeRegister, self).__init__()

	def __str__(self):
		if self.is_virtual():
			return 'gp-vreg<{0}>'.format(self.number)
		else:
			return self.name

	def __contains__(self, register):
		if self.is_virtual():
			return self.number == register.number
		else:
			if isinstance(self, GeneralPurposeRegister32):
				if self.name == register.name:
					return True
				elif self.get_word().name == register.name:
					return True
				elif self.name in ['eax', 'ebx', 'ecx', 'edx']:
					return self.get_low_byte().name == register.name
				else:
					return False
			elif isinstance(self, GeneralPurposeRegister16):
				if self.name == register.name:
					return True
				elif self.name in ['ax', 'bx', 'cx', 'dx']:
					return self.get_low_byte().name == register.name
				else:
					return False
			else:
				return self.name == register.name

class GeneralPurposeRegister32(GeneralPurposeRegister):
	def __init__(self, id = None):
		super(GeneralPurposeRegister32, self).__init__()
		if isinstance(id, str):
			if id in ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp']:
				self.name = id
				self.number = None
				self.type = 'general-purpose'
				self.size = 32
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, int) or isinstance(id, long):
			self.name = None
			self.number = id
			self.type = 'general-purpose'
			self.size = 32
		elif isinstance(id, GeneralPurposeRegister32):
			self.name = id.name
			self.number = id.number
			self.type = id.type
			self.size = id.size
		elif id is None:
			self.name = None
			self.number = current_function.allocate_general_purpose_register32()
			self.type = 'general-purpose'
			self.size = 32
		else:
			raise TypeError('Register id  is neither a name of an architectural general-purpose 32-bit register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'gp-vreg<{0}>'.format(self.number)
		else:
			return self.name

	def __add__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister32WithOffset(self, offset)
		else:
			raise TypeError('offset is not a integer number')

	def get_low_byte(self):
		if self.is_virtual():
			return GeneralPurposeRegister8(self.number)
		else:
			name_map = { 'eax': 'al', 'ebx': 'bl', 'ecx': 'cl', 'edx': 'dl'}
			if self.name in name_map.iterkeys():
				return GeneralPurposeRegister8(name_map[self.name])
			else:
				raise ValueError('The low byte can be explicitly addressed only for registers {0}'.format(", ".join(name_map.iterkeys())))

	def get_word(self):
		if self.is_virtual():
			return GeneralPurposeRegister16(self.number)
		else:
			name_map = { 'eax': 'ax', 'ebx': 'bx', 'ecx': 'cx', 'edx': 'dx', 'esi': 'si', 'edi': 'di', 'ebp': 'bp', 'esp': 'sp' }
			return GeneralPurposeRegister16(name_map[self.name])

eax = GeneralPurposeRegister32('eax')
ebx = GeneralPurposeRegister32('ebx')
ecx = GeneralPurposeRegister32('ecx')
edx = GeneralPurposeRegister32('edx')
esi = GeneralPurposeRegister32('esi')
edi = GeneralPurposeRegister32('edi')
ebp = GeneralPurposeRegister32('ebp')
esp = GeneralPurposeRegister32('esp')

class GeneralPurposeRegister32WithOffset(object):
	def __init__(self, register, offset):
		super(GeneralPurposeRegister32WithOffset, self).__init__()
		self.register = register
		self.offset = offset
		if not isinstance(register, GeneralPurposeRegister32):
			raise TypeError('register is not an instance of the 32-bit general-purpose register clas')
		if not isinstance(offset, int):
			raise TypeError('offset is not a integer number')

	def __add__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister32WithOffset(self.register, self.offset + offset)
		else:
			raise TypeError('offset is not a integer number')

	def __sub__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister32WithOffset(self.register, self.offset - offset)
		else:
			raise TypeError('offset is not a integer number')

	def __str__(self):
		if self.offset == 0:
			return str(self.register)
		else:
			return "{0} + {1}".format(self.register, self.offset)

class GeneralPurposeRegister16(GeneralPurposeRegister):
	def __init__(self, id = None):
		super(GeneralPurposeRegister16, self).__init__()
		if isinstance(id, str):
			if id in ['ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp']:
				self.name = id
				self.number = None
				self.type = 'general-purpose'
				self.size = 16
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, int) or isinstance(id, long):
			self.name = None
			self.number = id
			self.type = 'general-purpose'
			self.size = 16
		elif isinstance(id, GeneralPurposeRegister16):
			self.name = id.name
			self.number = id.number
			self.type = id.type
			self.size = id.size
		elif id is None:
			self.name = None
			self.number = current_function.allocate_general_purpose_register16()
			self.type = 'general-purpose'
			self.size = 16
		else:
			raise TypeError('Register id  is neither a name of an architectural general-purpose 16-bit register, nor an id of a virtual register')

	def get_low_byte(self):
		if self.is_virtual():
			return GeneralPurposeRegister8(self.number)
		else:
			name_map = { 'ax': 'al', 'bx': 'bl', 'cx': 'cl', 'dx': 'dl'}
			if self.name in name_map.iterkeys():
				return GeneralPurposeRegister8(name_map[self.name])
			else:
				raise ValueError('The low byte can be explicitly addressed only for registers {0}'.format(", ".join(name_map.iterkeys())))

ax = GeneralPurposeRegister16('ax')
bx = GeneralPurposeRegister16('bx')
cx = GeneralPurposeRegister16('cx')
dx = GeneralPurposeRegister16('dx')
si = GeneralPurposeRegister16('si')
di = GeneralPurposeRegister16('di')
bp = GeneralPurposeRegister16('bp')

class GeneralPurposeRegister8(GeneralPurposeRegister):
	def __init__(self, id = None):
		super(GeneralPurposeRegister8, self).__init__()
		if isinstance(id, str):
			if id in ['al', 'ah', 'bl', 'bh', 'cl', 'ch', 'dl', 'dh']:
				self.name = id
				self.number = None
				self.type = 'general-purpose'
				self.size = 8
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, int) or isinstance(id, long):
			self.name = None
			self.number = id
			self.type = 'general-purpose'
			self.size = 8
		elif isinstance(id, GeneralPurposeRegister8):
			self.name = id.name
			self.number = id.number
			self.type = id.type
			self.size = id.size
		elif id is None:
			self.name = None
			self.number = current_function.allocate_general_purpose_register8()
			self.type = 'general-purpose'
			self.size = 8
		else:
			raise TypeError('Register id  is neither a name of an architectural general-purpose 8-bit register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'gp8-vreg<{0}>'.format(self.number)
		else:
			return self.name

al = GeneralPurposeRegister8('al')
bl = GeneralPurposeRegister8('bl')
cl = GeneralPurposeRegister8('cl')
dl = GeneralPurposeRegister8('dl')
ah = GeneralPurposeRegister8('ah')
bh = GeneralPurposeRegister8('bh')
ch = GeneralPurposeRegister8('ch')
dh = GeneralPurposeRegister8('dh')

class MMXRegister(Register):
	def __init__(self, id = None):
		super(MMXRegister, self).__init__()
		if isinstance(id, str):
			if id in ['mm0', 'mm1', 'mm2', 'mm3', 'mm4', 'mm5', 'mm6', 'mm7']:
				self.name = id
				self.number = None
				self.type = 'mmx'
				self.size = 64
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, int) or isinstance(id, long):
			self.name = None
			self.number = id
			self.type = 'mmx'
			self.size = 64
		elif isinstance(id, MMXRegister):
			self.name = id.name
			self.number = id.number
			self.type = id.type
			self.size = id.size
		elif id is None:
			self.name = None
			self.number = current_function.allocate_mmx_register()
			self.type = 'mmx'
			self.size = 64
		else:
			raise TypeError('Register id is neither a name of an architectural mmx register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'mm-vreg<{0}>'.format(self.number)
		else:
			return self.name

mm0 = MMXRegister('mm0')
mm1 = MMXRegister('mm1')
mm2 = MMXRegister('mm2')
mm3 = MMXRegister('mm3')
mm4 = MMXRegister('mm4')
mm5 = MMXRegister('mm5')
mm6 = MMXRegister('mm6')
mm7 = MMXRegister('mm7')

class SSERegister(Register):
	def __init__(self, id = None):
		super(SSERegister, self).__init__()
		if isinstance(id, str):
			if id in ['xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7']:
				self.name = id
				self.number = None
				self.type = 'sse'
				self.size = 128
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, int) or isinstance(id, long):
			self.name = None
			self.number = id
			self.type = 'sse'
			self.size = 128
		elif isinstance(id, SSERegister):
			self.name = id.name
			self.number = id.number
			self.type = id.type
			self.size = id.size
		elif id is None:
			self.name = None
			self.number = current_function.allocate_sse_register()
			self.type = 'sse'
			self.size = 128
		else:
			raise TypeError('Register id is neither a name of an architectural sse register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'xmm-vreg<{0}>'.format(self.number)
		else:
			return self.name

xmm0 = SSERegister('xmm0')
xmm1 = SSERegister('xmm1')
xmm2 = SSERegister('xmm2')
xmm3 = SSERegister('xmm3')
xmm4 = SSERegister('xmm4')
xmm5 = SSERegister('xmm5')
xmm6 = SSERegister('xmm6')
xmm7 = SSERegister('xmm7')

class AVXRegister(Register):
	def __init__(self, id = None):
		super(AVXRegister, self).__init__()
		if isinstance(id, str):
			if id in ['ymm0', 'ymm1', 'ymm2', 'ymm3', 'ymm4', 'ymm5', 'ymm6', 'ymm7']:
				self.name = id
				self.number = None
				self.type = 'avx'
				self.size = 256
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, int) or isinstance(id, long):
			self.name = None
			self.number = id
			self.type = 'avx'
			self.size = 256
		elif isinstance(id, AVXRegister):
			self.name = id.name
			self.number = id.number
			self.type = id.type
			self.size = id.size
		elif id is None:
			self.name = None
			self.number = current_function.allocate_sse_register()
			self.type = 'avx'
			self.size = 256
		else:
			raise TypeError('Register id is neither a name of an architectural avx register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'ymm-vreg<{0}>'.format(self.number)
		else:
			return self.name

ymm0 = AVXRegister('ymm0')
ymm1 = AVXRegister('ymm1')
ymm2 = AVXRegister('ymm2')
ymm3 = AVXRegister('ymm3')
ymm4 = AVXRegister('ymm4')
ymm5 = AVXRegister('ymm5')
ymm6 = AVXRegister('ymm6')
ymm7 = AVXRegister('ymm7')

class Operand(object):
	def __init__(self, operand):
		super(Operand, self).__init__()
		if isinstance(operand, Register):
			self.type = 'register'
			self.register = operand
		elif isinstance(operand, int) or isinstance(operand, long):
			if -2147483648 <= operand <= 4294967295:
				self.type = 'immediate'
				self.immediate = operand
			else:
				raise ValueError('The immediate operand {0} is not a 32-bit value'.format(operand))
		elif isinstance(operand, list):
			if len(operand) == 1:
				address = operand[0]
				self.type = 'memory'
				self.size = None
				if isinstance(address, GeneralPurposeRegister32):
					self.base = address
					self.scale = 0
					self.index = None
					self.offset = 0
				elif isinstance(operand[0], GeneralPurposeRegister32WithOffset):
					self.base = address.register
					self.scale = 0
					self.index = None
					self.offset = address.offset
				else:
					raise TypeError('Memory operand must be a list with register or register + offset')
			else:
				raise ValueError('Memory operand must be a list with only one element')
		elif isinstance(operand, MemoryOperand):
			address = operand.address
			self.type = 'memory'
			self.size = operand.size
			if isinstance(address, GeneralPurposeRegister32):
				self.base = address
				self.scale = 0
				self.index = None
				self.offset = 0
			elif isinstance(address, GeneralPurposeRegister32WithOffset):
				self.base = address.register
				self.scale = 0
				self.index = None
				self.offset = address.offset
			else:
				raise TypeError('Memory operand must be a list with register or register + offset')
		elif isinstance(operand, Constant):
			self.type = 'constant'
			self.constant = operand
			self.size = operand.size * operand.repeats
		elif isinstance(operand, str):
			self.type = 'label'
			self.label = operand
		elif operand is None:
			self.type = 'none'
		else:
			raise TypeError('The operand {0} is not a valid assembly instruction operand'.format(operand))

	def __str__(self):
		if self.is_constant():
			size_specifier = MemoryOperandSizeSpecifier.size_to_name_map[self.size]
			return size_specifier + "[{0}]".format(self.constant.label)
		elif self.is_memory_address():
			size_specifier = ""
			if not self.size is None:
				size_specifier = MemoryOperandSizeSpecifier.size_to_name_map[self.size] + " "
			if self.offset == 0:
				return size_specifier + "[{0}]".format(self.base)
			elif -128 <= self.offset <= 127:
				return size_specifier + "[byte {0} + {1}]".format(self.base, self.offset)
			else:
				return size_specifier + "[dword {0} + {1}".format(self.base, self.offset)
		elif self.is_register():
			return str(self.register)
		elif self.is_label():
			return self.label
		elif self.is_immediate():
			return str(self.immediate)
		elif self.is_constant():
			return str(self.constant)
		elif self.is_none():
			return ""
		else:
			raise TypeError('Unsupported operand type')

	def __eq__(self, other):
		if isinstance(other, Operand):
			if self.type == other.type:
				if self.is_immediate():
					return self.immediate == other.immediate
				elif self.is_register():
					return self.register == other.register
				elif self.is_memory_address():
					return self.base == other.base and self.offset == other.offset
				elif self.is_label():
					return self.label == other.label
				else:
					return False
			else:
				return False
		else:
			return False

	def is_none(self):
		return self.type == 'none'

	def is_immediate(self):
		return self.type == 'immediate'

	def is_int32(self):
		return self.is_immediate()

	def is_int16(self):
		if self.type == 'immediate':
			if -32768 <= self.immediate <= 65535:
				return True
			else:
				return False
		else:
			return False

	def is_uint16(self):
		if self.type == 'immediate':
			if 0 <= self.immediate <= 65535:
				return True
			else:
				return False
		else:
			return False

	def is_int8(self):
		if self.type == 'immediate':
			if -128 <= self.immediate <= 255:
				return True
			else:
				return False
		else:
			return False

	def is_uint8(self):
		if self.type == 'immediate':
			if 0 <= self.immediate <= 255:
				return True
			else:
				return False
		else:
			return False

	def is_sint8(self):
		if self.type == 'immediate':
			if -128 <= self.immediate <= 127:
				return True
			else:
				return False
		else:
			return False

	def is_label(self):
		return self.type == 'label'

	def is_constant(self):
		return self.type == 'constant'

	def is_register(self):
		return self.type == 'register'

	def is_general_purpose_register(self):
		if self.type == 'register':
			if isinstance(self.register, GeneralPurposeRegister):
				return True
			else:
				return False
		else:
			return False

	def is_general_purpose_register32(self):
		if self.type == 'register':
			if isinstance(self.register, GeneralPurposeRegister32):
				return True
			else:
				return False
		else:
			return False

	def is_general_purpose_register16(self):
		if self.type == 'register':
			if isinstance(self.register, GeneralPurposeRegister16):
				return True
			else:
				return False
		else:
			return False

	def is_general_purpose_register8(self):
		if self.type == 'register':
			if isinstance(self.register, GeneralPurposeRegister8):
				return True
			else:
				return False
		else:
			return False

	def is_mmx_register(self):
		if self.type == 'register':
			if isinstance(self.register, MMXRegister):
				return True
			else:
				return False
		else:
			return False

	def is_sse_register(self):
		if self.type == 'register':
			if isinstance(self.register, SSERegister):
				return True
			else:
				return False
		else:
			return False

	def is_avx_register(self):
		if self.type == 'register':
			if isinstance(self.register, AVXRegister):
				return True
			else:
				return False
		else:
			return False

	def is_memory_address(self):
		return self.type == 'memory' or self.type == 'constant'

	def is_memory_address256(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 256
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 256
		else:
			return False

	def is_memory_address128(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 128
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 128
		else:
			return False

	def is_memory_address80(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 80
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 80
		else:
			return False

	def is_memory_address64(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 64
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 64
		else:
			return False

	def is_memory_address32(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 32
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 32
		else:
			return False

	def is_memory_address16(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 16
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 16
		else:
			return False

	def is_memory_address8(self, strict_size = False):
		if self.type == 'memory':
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 8
		elif self.type == 'constant':
			return self.constant.size * self.constant.repeats == 8
		else:
			return False

	def get_modrm_extra_length(self):
		if self.is_register():
			return 0 # encoded in ModR/M, no extra bytes needed
		elif self.is_constant():
			return 4 # 4 bytes for offset
		elif self.is_memory_address():
			if self.offset == 0:
				if self.base.name == 'ebp':
					return 1 # ebp + 0 is encoded
				elif self.base.name == 'esp':
					return 1 # esp is encoded in SIB
				else:
					return 0 # encoded in ModR/M, no extra bytes needed
			elif -128 <= self.offset <= 127:
				if self.base.name == 'esp':
					return 1 + 1 # esp is encoded in SIB + 1 byte for offset
				else:
					return 1 # 1 byte for offset
			else:
				if self.base.name == 'esp':
					return 4 + 1 # esp is encoded in SIB + 4 bytes for offset
				else:
					return 4 # 4 bytes for offset
		else:
			raise ValueError('The operand can not be encoded in ModR/M')

	def get_registers_list(self):
		if self.is_register():
			return [self.register]
		elif self.is_constant():
			return list()
		elif self.is_memory_address():
			return [self.base]
		else:
			return list()

class MemoryOperand(object):
	def __init__(self, address, size):
		super(MemoryOperand, self).__init__()
		check_generic_memory_operand(address)
		self.address = address
		if isinstance(size, int):
			self.size = size
		else:
			raise TypeError('The size of the memory operand must be an integer')

	def __str__(self):
		return str(Operand(self))

class MemoryOperandSizeSpecifier(object):
	def __init__(self, size):
		super(MemoryOperandSizeSpecifier, self).__init__()
		if isinstance(size, int):
			if size in self.size_to_name_map.iterkeys():
				self.size = size
			else:
				raise ValueError('The size of memory operand size specifier ({0}) is not in the list of supported memory operand size specifiers ({1})',
					size, ", ".join(map(str, self.size_to_name_map.iterkeys())))
		else:
			raise TypeError('The size of memory operand size specifier must be an integer')

	def __str__(self):
		return self.size_to_name_map[self.size]

	def __getitem__(self, address):
		if isinstance(address, GeneralPurposeRegister32):
			return MemoryOperand(address, self.size)
		elif isinstance(address, GeneralPurposeRegister32WithOffset):
			return MemoryOperand(address, self.size)
		else:
			raise TypeError('Memory address must be either a register or register + offset')

	size_to_name_map = {8: 'byte', 16: 'word', 32: 'dword', 64: 'qword', 80: 'tword', 128: 'oword', 256: 'hword'}


byte = MemoryOperandSizeSpecifier(8)
word16 = MemoryOperandSizeSpecifier(16)
word = MemoryOperandSizeSpecifier(16)
word32 = MemoryOperandSizeSpecifier(32)
dword = MemoryOperandSizeSpecifier(32)
word64 = MemoryOperandSizeSpecifier(64)
qword = MemoryOperandSizeSpecifier(64)
word80 = MemoryOperandSizeSpecifier(80)
tword = MemoryOperandSizeSpecifier(80)
word128 = MemoryOperandSizeSpecifier(128)
oword = MemoryOperandSizeSpecifier(128)
word256 = MemoryOperandSizeSpecifier(256)
hword = MemoryOperandSizeSpecifier(256)

def check_generic_memory_operand(operand):
	if isinstance(operand, list):
		if len(operand) == 1:
			if isinstance(operand[0], GeneralPurposeRegister32):
				return
			elif isinstance(operand[0], GeneralPurposeRegister32WithOffset):
				return
			else:
				raise TypeError('Memory operand must be a list with register or register + offset')
		else:
			raise ValueError('Memory operand must be a list with only one element')
	else:
		return

class QuasiInstruction(object):
	def __init__(self, name):
		super(QuasiInstruction, self).__init__()
		self.name = name
		self.basic_block = None

class Instruction(QuasiInstruction):
	def __init__(self, name, isa_extension = None):
		super(Instruction, self).__init__(name)
		if(not isa_extension is None) and (not isa_extension in supported_isa_extensions):
			raise ValueError('Instruction ISA extension {0} in not in the supported ISA extensions list ({1})'.format(isa_extension, ", ".join(supported_isa_extensions)))
		self.isa_extension = isa_extension
		self.short_eax_form = False
		self.available_registers = set()
		self.live_registers = set()

	def __len__(self):
		return self.size

	def __str__(self):
		return str(self.name)

	def get_isa_extension(self):
		return self.isa_extension

class BinaryInstruction(Instruction):
	def __init__(self, name, destination, source, isa_extension = None):
		super(BinaryInstruction, self).__init__(name, isa_extension)
		self.name = name
		self.destination = destination
		self.source = source

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

class Label(QuasiInstruction):
	def __init__(self, name):
		super(Label, self).__init__('<LABEL>')
		self.name = name
		self.input_branches = set()

	def __str__(self):
		return "." + self.name + ':'

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return list()

class AlignQuasiInstruction(QuasiInstruction):
	supported_alignments = [2, 4, 8, 16, 32]

	def __init__(self, alignment):
		super(AlignQuasiInstruction, self).__init__('<ALIGN>')
		if isinstance(alignment, int):
			if alignment in AlignQuasiInstruction.supported_alignments:
				self.alignment = alignment
			else:
				raise ValueError("The alignment value {0} is not in the list of supported alignments ({1})".format(alignment, ", ".join(AlignQuasiInstruction.supported_alignments)))
		else:
			raise TypeError("The alignment value must be an integer")

	def __str__(self):
		return "align {0}".format(self.alignment)

class LoadConstantPseudoInstruction(Instruction):
	def __init__(self, destination, source):
		super(LoadConstantPseudoInstruction, self).__init__('<LOAD-CONSTANT>')
		if destination.is_register():
			self.destination = destination
		else:
			raise ValueError('Load constant pseudo-instruction expects a register as a destination')
		if source.is_constant():
			if destination.register.size == source.constant.size * source.constant.repeats:
				self.source = source
			else:
				raise ValueError('The size of constant should be the same as the size of register')
		else:
			raise ValueError('Load constant pseudo-instruction expects a Constant instance as a source')
		self.size = 4 + 4

	def __str__(self):
		return "LOAD.CONSTANT {0} = {1}".format(self.destination, self.source)

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return [self.destination.register]

class LoadParameterPseudoInstruction(Instruction):
	def __init__(self, destination, source):
		super(LoadParameterPseudoInstruction, self).__init__('<LOAD-PARAMETER>')
		if destination.is_general_purpose_register32():
			self.destination = destination
		else:
			raise ValueError('Load parameter pseudo-instruction expects a general-purpose 32-bit register as a destination')
		if isinstance(source, str):
			if current_function.has_parameter(source):
				self.parameter = source
			else:
				raise ValueError('{0} is not an argument of the currently active function'.format(source))
		else:
			raise TypeError('Load parameter pseudo-instruction expects a string parameter name as a source')
		# MOV r32/m32, r32: 8B /r
		self.size = 2 + 1 + 1 # 1-byte opcode + ModR/M + SIB (esp addressing) + 8-bit offset

	def __str__(self):
		return "LOAD.PARAMETER {0} = {1}".format(self.destination, self.parameter)

	def get_input_registers_list(self):
		return [esp]

	def get_output_registers_list(self):
		return [self.destination.register]

class ArithmeticInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		super(ArithmeticInstruction, self).__init__(name, destination, source)
		allowed_instructions = ['ADD', 'ADC', 'SUB', 'SBB', 'CMP', 'TEST', 'AND', 'OR', 'XOR']
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# ADD r32, r32/m32: 03 /r
			# ADC r32, r32/m32: 13 /r
			# SUB r32, r32/m32: 2B /r
			# SBB r32, r32/m32: 1B /r
			# CMP r32, r32/m32: 3B /r
			# AND r32, r32/m32: 23 /r
			# OR  r32, r32/m32: 0B /r
			# XOR r32, r32/m32: 33 /r
			self.size = 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()):
			# ADD r16, r16/m16: 66 03 /r
			# ADC r16, r16/m16: 66 13 /r
			# SUB r16, r16/m16: 66 2B /r
			# SBB r16, r16/m16: 66 1B /r
			# CMP r16, r16/m16: 66 3B /r
			# AND r16, r16/m16: 66 23 /r
			# OR  r16, r16/m16: 66 0B /r
			# XOR r16, r16/m16: 66 33 /r
			self.size = 1 + 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register8() and (source.is_general_purpose_register8() or source.is_memory_address8()):
			# ADD r8, r8/m8: 03 /r
			# ADC r8, r8/m8: 13 /r
			# SUB r8, r8/m8: 2B /r
			# SBB r8, r8/m8: 1B /r
			# CMP r8, r8/m8: 3B /r
			# AND r8, r8/m8: 22 /r
			# OR  r8, r8/m8: 0A /r
			# XOR r8, r8/m8: 32 /r
			self.size = 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and source.is_int32():
			if name != 'TEST' and source.is_sint8():
				# ADD r32/m32, imm8: 83 /0 ib
				# ADC r32/m32, imm8: 83 /2 ib
				# SUB r32/m32, imm8: 83 /5 ib
				# SBB r32/m32, imm8: 83 /3 ib
				# CMP r32/m32, imm8: 83 /7 ib
				# AND r32/m32, imm8: 83 /4 ib
				# OR  r32/m32, imm8: 83 /1 ib
				# XOR r32/m32, imm8: 83 /6 ib
				self.size = 2 + 1 + destination.get_modrm_extra_length()
			else:
				if destination == eax:
					# ADD  eax, imm32: 05 id
					# ADC  eax, imm32: 15 id
					# SUB  eax, imm32: 2D id
					# SBB  eax, imm32: 1D id
					# CMP  eax, imm32: 3D id
					# AND  eax, imm32: 25 id
					# OR   eax, imm32: 0D id
					# XOR  eax, imm32: 35 id
					# TEST eax, imm32: A9 id
					self.size = 1 + 4
				else:
					# ADD  r32/m32, imm32: 81 /0 id
					# ADC  r32/m32, imm32: 81 /2 id
					# SUB  r32/m32, imm32: 81 /5 id
					# SBB  r32/m32, imm32: 81 /3 id
					# CMP  r32/m32, imm32: 81 /7 id
					# AND  r32/m32, imm32: 81 /4 id
					# OR   r32/m32, imm32: 81 /1 id
					# XOR  r32/m32, imm32: 81 /6 id
					# TEST r32/m32, imm32: F7 /0 id
					self.size = 2 + 4
			self.short_eax_form = name != 'TEST'
		elif destination.is_general_purpose_register16() and source.is_int16():
			if name != 'TEST' and source.is_sint8():
				# ADD r16/m16, imm8: 66 83 /0 ib
				# ADC r16/m16, imm8: 66 83 /2 ib
				# SUB r16/m16, imm8: 66 83 /5 ib
				# SBB r16/m16, imm8: 66 83 /3 ib
				# CMP r16/m16, imm8: 66 83 /7 ib
				# AND r16/m16, imm8: 66 83 /4 ib
				# OR  r16/m16, imm8: 66 83 /1 ib
				# XOR r16/m16, imm8: 66 83 /6 ib
				self.size = 1 + 2 + 1 + destination.get_modrm_extra_length()
			else:
				if destination == ax:
					# ADD  ax, imm16: 66 05 iw
					# ADC  ax, imm16: 66 15 iw
					# SUB  ax, imm16: 66 2D iw
					# SBB  ax, imm16: 66 1D iw
					# CMP  ax, imm16: 66 3D iw
					# AND  ax, imm16: 66 25 iw
					# OR   ax, imm16: 66 0D iw
					# XOR  ax, imm16: 66 35 iw
					# TEST ax, imm16: 66 A9 iw
					self.size = 1 + 1 + 2
				else:
					# ADD  r16/m16, imm16: 66 81 /0 iw
					# ADC  r16/m16, imm16: 66 81 /2 iw
					# SUB  r16/m16, imm16: 66 81 /5 iw
					# SBB  r16/m16, imm16: 66 81 /3 iw
					# CMP  r16/m16, imm16: 66 81 /7 iw
					# AND  r16/m16, imm16: 66 81 /4 iw
					# OR   r16/m16, imm16: 66 81 /1 iw
					# XOR  r16/m16, imm16: 66 81 /6 iw
					# TEST r16/m16, imm16: 66 F7 /0 iw
					self.size = 1 + 2 + 2
			self.short_eax_form = name != 'TEST'
		elif destination.is_general_purpose_register8() and source.is_int8():
			if destination == al:
				# ADD  al, imm8: 05 ib
				# ADC  al, imm8: 15 ib
				# SUB  al, imm8: 2D ib
				# SBB  al, imm8: 1D ib
				# CMP  al, imm8: 3D ib
				# AND  al, imm8: 25 ib
				# OR   al, imm8: 0D ib
				# XOR  al, imm8: 34 ib
				# TEST al, imm8: A8 ib
				self.size = 1 + 1
			else:
				# ADD  r8/m8, imm8: 80 /0 ib
				# ADC  r8/m8, imm8: 80 /2 ib
				# SUB  r8/m8, imm8: 80 /5 ib
				# SBB  r8/m8, imm8: 80 /3 ib
				# CMP  r8/m8, imm8: 80 /7 ib
				# AND  r8/m8, imm8: 80 /4 ib
				# OR   r8/m8, imm8: 80 /1 ib
				# XOR  r8/m8, imm8: 80 /6 ib
				# TEST r8/m8, imm8: F6 /0 ib
				self.size = 2 + 1
			self.short_eax_form = True
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		if self.name in ['XOR', 'SUB'] and self.source == self.destination:
			return list()
		else:
			input_registers_list = list()
			input_registers_list.extend(self.destination.get_registers_list())
			input_registers_list.extend(self.source.get_registers_list())
			return input_registers_list

	def get_output_registers_list(self):
		if self.name in ['CMP', 'TEST']:
			return list()
		else:
			if self.destination.is_register():
				return [self.destination.register]
			else:
				return list()

class ShiftInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		super(ShiftInstruction, self).__init__(name, destination, source)
		allowed_instructions = ['SHR', 'SAR', 'SHL', 'ROR', 'ROL', 'ROR', 'RCL', 'RCR']
		if not self.name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if (destination.is_general_purpose_register8() or destination.is_memory_address8()) and source.is_int8():
			if source.immediate == 1:
				# ROL r8/m8, 1: D0 /0
				# ROR r8/m8, 1: D0 /1
				# RCL r8/m8, 1: D0 /2
				# RCR r8/m8, 1: D0 /3
				# SHL r8/m8, 1: D0 /4
				# SHR r8/m8, 1: D0 /5
				# SAR r8/m8, 1: D0 /7
				self.size = 2 + destination.get_modrm_extra_length()
			else:
				# ROL r8/m8, imm8: C0 /0 ib
				# ROR r8/m8, imm8: C0 /1 ib
				# RCL r8/m8, imm8: C0 /2 ib
				# RCR r8/m8, imm8: C0 /3 ib
				# SHL r8/m8, imm8: C0 /4 ib
				# SHR r8/m8, imm8: C0 /5 ib
				# SAR r8/m8, imm8: C0 /7 ib
				self.size = 2 + 1 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16()) and source.is_int8():
			if source.immediate == 1:
				# ROL r16/m16, 1: 66 D1 /0
				# ROR r16/m16, 1: 66 D1 /1
				# RCL r16/m16, 1: 66 D1 /2
				# RCR r16/m16, 1: 66 D1 /3
				# SHL r16/m16, 1: 66 D1 /4
				# SHR r16/m16, 1: 66 D1 /5
				# SAR r16/m16, 1: 66 D1 /7
				self.size = 1 + 2 + destination.get_modrm_extra_length()
			else:
				# ROL r16/m16, imm8: 66 C1 /0 ib
				# ROR r16/m16, imm8: 66 C1 /1 ib
				# RCL r16/m16, imm8: 66 C1 /2 ib
				# RCR r16/m16, imm8: 66 C1 /3 ib
				# SHL r16/m16, imm8: 66 C1 /4 ib
				# SHR r16/m16, imm8: 66 C1 /5 ib
				# SAR r16/m16, imm8: 66 C1 /7 ib
				self.size = 1 + 2 + 1 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32()) and source.is_int8():
			if source.immediate == 1:
				# ROL r32/m32, 1: D1 /0
				# ROR r32/m32, 1: D1 /1
				# RCL r32/m32, 1: D1 /2
				# RCR r32/m32, 1: D1 /3
				# SHL r32/m32, 1: D1 /4
				# SHR r32/m32, 1: D1 /5
				# SAR r32/m32, 1: D1 /7
				self.size = 2 + destination.get_modrm_extra_length()
			else:
				# ROL r32/m32, imm8: C1 /0 ib
				# ROR r32/m32, imm8: C1 /1 ib
				# RCL r32/m32, imm8: C1 /2 ib
				# RCR r32/m32, imm8: C1 /3 ib
				# SHL r32/m32, imm8: C1 /4 ib
				# SHR r32/m32, imm8: C1 /5 ib
				# SAR r32/m32, imm8: C1 /7 ib
				self.size = 2 + 1 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register8() or destination.is_memory_address8()) and source.is_general_purpose_register():
			if source.register == ecx or source.register == cx or source.register == cl or source.register.is_virtual():
				# ROL r8/m8, cl: D2 /0 ib
				# ROR r8/m8, cl: D2 /1 ib
				# RCL r8/m8, cl: D2 /2 ib
				# RCR r8/m8, cl: D2 /3 ib
				# SHL r8/m8, cl: D2 /4 ib
				# SHR r8/m8, cl: D2 /5 ib
				# SAR r8/m8, cl: D2 /7 ib
				self.size = 2 + 1 + destination.get_modrm_extra_length()
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16()) and source.is_general_purpose_register():
			if source.register == ecx or source.register == cx or source.register == cl or source.register.is_virtual():
				# ROL r16/m16, cl: 66 D3 /0
				# ROR r16/m16, cl: 66 D3 /1
				# RCL r16/m16, cl: 66 D3 /2
				# RCR r16/m16, cl: 66 D3 /3
				# SHL r16/m16, cl: 66 D3 /4
				# SHR r16/m16, cl: 66 D3 /5
				# SAR r16/m16, cl: 66 D3 /7
				self.size = 1 + 2 + destination.get_modrm_extra_length()
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32()) and source.is_general_purpose_register():
			if source.register == ecx or source.register == cx or source.register == cl or source.register.is_virtual():
				# RCL r32/m32, cl: D3 /2
				# RCR r32/m32, cl: D3 /3
				# SHL r32/m32, cl: D3 /4
				# SHR r32/m32, cl: D3 /5
				# SAR r32/m32, cl: D3 /7
				self.size = 2 + destination.get_modrm_extra_length()
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

class BitTestInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		super(BitTestInstruction, self).__init__(name,  destination, source)
		allowed_instructions = ['BT', 'BTS', 'BTR', 'BTC']
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if (destination.is_general_purpose_register32() or destination.is_memory_address32()) and source.is_general_purpose_register32():
			#  BT m32/r32, r32: 0F A3 /r
			# BTS m32/r32, r32: 0F AB /r
			# BTR m32/r32, r32: 0F B3 /r
			# BTC m32/r32, r32: 0F BB /r
			self.size = 3 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16()) and source.is_general_purpose_register16():
			#  BT m16/r16, r16: 66 0F A3 /r
			# BTS m16/r16, r16: 66 0F AB /r
			# BTR m16/r16, r16: 66 0F B3 /r
			# BTC m16/r16, r16: 66 0F BB /r
			self.size = 1 + 3 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32()) and source.is_uint8():
			#  BT m32/r32, imm8: 0F BA /4 ib
			# BTS m32/r32, imm8: 0F BA /5 ib
			# BTR m32/r32, imm8: 0F BA /6 ib
			# BTC m32/r32, imm8: 0F BA /7 ib
			self.size = 3 + 1 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16()) and source.is_uint8():
			#  BT m16/r16, imm8: 66 0F BA /4 ib
			# BTS m16/r16, imm8: 66 0F BA /5 ib
			# BTR m16/r16, imm8: 66 0F BA /6 ib
			# BTC m16/r16, imm8: 66 0F BA /7 ib
			self.size = 1 + 3 + 1 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.destination.is_general_purpose_register() and name != "BT":
			return [self.destination.register]
		else:
			return list()

class ImulInstruction(Instruction):
	def __init__(self, destination, source, immediate):
		super(ImulInstruction, self).__init__("IMUL")
		if (destination.is_general_purpose_register8() or destination.is_memory_address8(strict_size = True)) and source.is_none() and immediate.is_none():
			# IMUL r8/m8: F6 /5
			self.operands = 1
			self.source = destination
			self.size = 2 + self.source.get_modrm_extra_length()
			self.output_registers_list = [ax]
			self.input_registers_list = [al]
			self.input_registers_list.append(self.source.get_registers_list())
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16(strict_size = True)) and source.is_none() and immediate.is_none():
			# IMUL r16/m16: 66 F7 /5
			self.operands = 1
			self.source = destination
			self.size = 1 + 2 + self.source.get_modrm_extra_length()
			self.output_registers_list = [dx, ax]
			self.input_registers_list = [ax]
			self.input_registers_list.append(self.source.get_registers_list())
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32(strict_size = True)) and source.is_none() and immediate.is_none():
			# IMUL r32/m32: F7 /5
			self.operands = 1
			self.source = destination
			self.size = 2 + self.source.get_modrm_extra_length()
			self.output_registers_list = [edx, eax]
			self.input_registers_list = [eax]
			self.input_registers_list.append(self.source.get_registers_list())
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()) and immediate.is_none():
			# IMUL r16, r16/m16: 66 0F AF /r
			self.operands = 2
			self.source = source
			self.destination = destination
			self.size = 1 + 3 + source.get_modrm_extra_length()
			self.output_registers_list = destination.get_registers_list()
			self.input_registers_list = destination.get_registers_list() + source.get_registers_list()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()) and immediate.is_none():
			# IMUL r32, r32/m32: 0F AF /r
			self.operands = 2
			self.source = source
			self.destination = destination
			self.size = 3 + source.get_modrm_extra_length()
			self.output_registers_list = destination.get_registers_list()
			self.input_registers_list = destination.get_registers_list() + source.get_registers_list()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()) and immediate.is_int16():
			# IMUL r16, r16/m16,  imm8: 66 6B /r ib
			# IMUL r16, r16/m16, imm16: 66 69 /r iw
			self.operands = 3
			self.source = source
			self.destination = destination
			self.immediate = immediate
			if immediate.is_sint8():
				self.size = 1 + 2 + source.get_modrm_extra_length() + 1
			else:
				self.size = 1 + 2 + source.get_modrm_extra_length() + 2
			self.output_registers_list = destination.get_registers_list()
			self.input_registers_list = source.get_registers_list()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()) and immediate.is_int32():
			# IMUL r32, r32/m32,  imm8: 6B /r ib
			# IMUL r32, r32/m32, imm32: 69 /r id
			self.operands = 3
			self.source = source
			self.destination = destination
			self.immediate = immediate
			if immediate.is_sint8():
				self.size = 2 + source.get_modrm_extra_length() + 1
			else:
				self.size = 2 + source.get_modrm_extra_length() + 4
			self.output_registers_list = destination.get_registers_list()
			self.input_registers_list = source.get_registers_list()
		else:
			raise ValueError('Invalid operands in instruction IMUL {0}, {1}, {2}'.format(destination, source, immediate))

	def __str__(self):
		if self.operands == 1:
			return "IMUL {0}".format(self.source)
		elif self.operands == 2:
			return "IMUL {0}, {1}".format(self.source, self.destination)
		else:
			return "IMUL {0}, {1}, {2}".format(self.source, self.destination, self.immediate)

	def get_input_registers_list(self):
		return self.input_registers_list

	def get_output_registers_list(self):
		return self.output_registers_list

class MulInstruction(Instruction):
	def __init__(self, source):
		super(MulInstruction, self).__init__("MUL")
		if source.is_general_purpose_register8() or source.is_memory_address8():
			# MUL r8/m8: F6 /4
			self.source = source
			self.input_registers_list = self.source.get_registers_list() + [al]
			self.output_registers_list = [ax]
		elif source.is_general_purpuse_register16() or source.is_memory_address16():
			# MUL r16/m16: 66 F7 /4
			self.source = source
			self.input_registers_list = self.source.get_registers_list() + [ax]
			self.output_registers_list = [ax, dx]
		elif source.is_general_purpose_register32() or source.is_memory_address32():
			# MUL r32/m32: F7 /4
			self.source = source
			self.input_registers_list = self.source.get_registers_list() + [eax]
			self.output_registers_list = [eax, edx]
		else:
			raise ValueError('Invalid operands in instruction MUL {0}'.format(source))

	def __str__(self):
		return "MUL {0}".format(self.source)

	def get_input_registers_list(self):
		return self.input_registers_list

	def get_output_registers_list(self):
		return self.output_registers_list

class MoveExtendInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		super(MoveExtendInstruction, self).__init__(name, destination, source)
		allowed_instructions = ['MOVZX', 'MOVSX']
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register32() and (source.is_general_purpose_register8() or source.is_memory_address8(strict_size=True)):
			# MOVZX r32, r8/m8: 0F B6 /r
			# MOVSX r32, r8/m8: 0F BE /r
			self.size = 3 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register8() or source.is_memory_address8(strict_size=True)):
			# MOVZX r16, r8/m8: 66 0F B6 /r
			# MOVSX r16, r8/m8: 66 0F BE /r
			self.size = 3 + 1 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register16() or source.is_memory_address16(strict_size=True)):
			# MOVZX r32, r16/m16: 0F B7 /r
			# MOVSX r32, r16/m16: 0F BF /r
			self.size = 3 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		input_registers_list = list()
		input_registers_list.extend(self.source.get_registers_list())
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

class MovInstruction(BinaryInstruction):
	def __init__(self, destination, source):
		super(MovInstruction, self).__init__('MOV', destination, source)
		if destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# MOV r32, r32/m32: 8B /r
			self.size = 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()):
			# MOV r16, r16/m16: 66 8B /r
			self.size = 1 + 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register8() and (source.is_general_purpose_register8() or source.is_memory_address8()):
			# MOV r8, r8/m8: 8A /r
			self.size = 2 + source.get_modrm_extra_length()
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32()) and source.is_general_purpose_register32():

			# MOV r32/m32, r32: 89 /r
			self.size = 2 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16()) and source.is_general_purpose_register16():
			# MOV r16/m16, r16: 66 89 /r
			self.size = 1 + 2 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register8() or destination.is_memory_address8()) and source.is_general_purpose_register8():
			# MOV r8/m8, r8: 88 /r
			self.size = 2 + destination.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and source.is_int32():
			# MOV r32, imm32: B8 +rd id
			self.size = 1 + 4
		elif destination.is_general_purpose_register16() and source.is_int16():
			# MOV r16, imm16: 66 B8 +rw iw
			self.size = 1 + 1 + 2
		elif destination.is_general_purpose_register8() and source.is_int8():
			# MOV r8, imm8: B0 +rb ib
			self.size = 1 + 1
		elif destination.is_memory_operand32(strict_size = True) and source.is_int32():
			# MOV r32/m32, imm32: C7 /0 id
			self.size = 2 + 4 + destination.get_modrm_extra_length()
		elif destination.is_memory_operand16(strict_size = True) and source.is_int16():
			# MOV r16/m16, imm16: 66 C7 /0 iw
			self.size = 1 + 2 + 2 + destination.get_modrm_extra_length()
		elif destination.is_memory_operand8(strict_size = True) and source.is_int8():
			# MOV r8/m8, imm8: C6 /0 ib
			self.size = 2 + 1 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction MOV {0}, {1}'.format(destination, source))

	def get_input_registers_list(self):
		input_registers_list = list()
		input_registers_list.extend(self.source.get_registers_list())
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

class ConditionalJumpInstruction(Instruction):
	def __init__(self, name, destination):
		super(ConditionalJumpInstruction, self).__init__(name)
		allowed_instructions = [ 'JA',  'JAE',  'JB',  'JBE',  'JC',  'JE',  'JG',  'JGE',  'JL',  'JLE',  'JO',  'JP',  'JPO',  'JS',  'JZ',
								'JNA', 'JNAE', 'JNB', 'JNBE', 'JNC', 'JNE', 'JNG', 'JNGE', 'JNL', 'JNLE', 'JNO', 'JNP', 'JNPO', 'JNS', 'JNZ']
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_label():
			self.destination = destination.label
			#   JA rel32: 0F 87 cd
			#  JAE rel32: 0F 83 cd
			#   JB rel32: 0F 82 cd
			#  JBE rel32: 0F 86 cd
			#   JC rel32: 0F 82 cd
			#   JE rel32: 0F 84 cd
			#   JZ rel32: 0F 84 cd
			self.size = 2 + 4
			self.is_visited = False
		else:
			raise TypeError('Only string names are accepted as destination labels')

	def __str__(self):
		return "{0} .{1}".format(self.name, self.destination)

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return list()

class CmovInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		super(CmovInstruction, self).__init__(name,  destination, source, 'CMOV')
		allowed_instructions = [ 'CMOVA',  'CMOVAE',  'CMOVB',  'CMOVBE',  'CMOVC',  'CMOVE',  'CMOVG',  'CMOVGE',  'CMOVL',  'CMOVLE',  'CMOVO',  'CMOVP',  'CMOVPO',  'CMOVS',  'CMOVZ',
								'CMOVNA', 'CMOVNAE', 'CMOVNB', 'CMOVNBE', 'CMOVNC', 'CMOVNE', 'CMOVNG', 'CMOVNGE', 'CMOVNL', 'CMOVNLE', 'CMOVNO', 'CMOVNP', 'CMOVNPO', 'CMOVNS', 'CMOVNZ']
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			#   CMOVA r32, r32/m32: 0F 47 /r
			#  CMOVAE r32, r32/m32: 0F 43 /r
			#   CMOVB r32, r32/m32: 0F 42 /r
			#  CMOVBE r32, r32/m32: 0F 46 /r
			#   CMOVC r32, r32/m32: 0F 42 /r
			#   CMOVE r32, r32/m32: 0F 44 /r
			#   CMOVG r32, r32/m32: 0F 4F /r
			#  CMOVGE r32, r32/m32: 0F 4D /r
			#   CMOVL r32, r32/m32: 0F 4C /r
			#  CMOVLE r32, r32/m32: 0F 4E /r
			#  CMOVNA r32, r32/m32: 0F 46 /r
			# CMOVNAE r32, r32/m32: 0F 42 /r
			#  CMOVNB r32, r32/m32: 0F 43 /r
			# CMOVNBE r32, r32/m32: 0F 47 /r
			#  CMOVNC r32, r32/m32: 0F 43 /r
			#  CMOVNE r32, r32/m32: 0F 45 /r
			#  CMOVNG r32, r32/m32: 0F 4E /r
			# CMOVNGE r32, r32/m32: 0F 4C /r
			#  CMOVNL r32, r32/m32: 0F 4D /r
			# CMOVNLE r32, r32/m32: 0F 4F /r
			#  CMOVNO r32, r32/m32: 0F 41 /r
			#  CMOVNP r32, r32/m32: 0F 4B /r
			#  CMOVNS r32, r32/m32: 0F 49 /r
			#  CMOVNZ r32, r32/m32: 0F 45 /r
			#   CMOVO r32, r32/m32: 0F 40 /r
			#   CMOVP r32, r32/m32: 0F 4A /r
			#  CMOVPE r32, r32/m32: 0F 4A /r
			#  CMOVPO r32, r32/m32: 0F 4B /r
			#   CMOVS r32, r32/m32: 0F 48 /r
			#   CMOVZ r32, r32/m32: 0F 44 /r
			self.destination = destination
			self.source = source
			self.size = 3 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()):
			#   CMOVA r16, r16/m16: 66 0F 47 /r
			#  CMOVAE r16, r16/m16: 66 0F 43 /r
			#   CMOVB r16, r16/m16: 66 0F 42 /r
			#  CMOVBE r16, r16/m16: 66 0F 46 /r
			#   CMOVC r16, r16/m16: 66 0F 42 /r
			#   CMOVE r16, r16/m16: 66 0F 44 /r
			#   CMOVG r16, r16/m16: 66 0F 4F /r
			#  CMOVGE r16, r16/m16: 66 0F 4D /r
			#   CMOVL r16, r16/m16: 66 0F 4C /r
			#  CMOVLE r16, r16/m16: 66 0F 4E /r
			#  CMOVNA r16, r16/m16: 66 0F 46 /r
			# CMOVNAE r16, r16/m16: 66 0F 42 /r
			#  CMOVNB r16, r16/m16: 66 0F 43 /r
			# CMOVNBE r16, r16/m16: 66 0F 47 /r
			#  CMOVNC r16, r16/m16: 66 0F 43 /r
			#  CMOVNE r16, r16/m16: 66 0F 45 /r
			#  CMOVNG r16, r16/m16: 66 0F 4E /r
			# CMOVNGE r16, r16/m16: 66 0F 4C /r
			#  CMOVNL r16, r16/m16: 66 0F 4D /r
			# CMOVNLE r16, r16/m16: 66 0F 4F /r
			#  CMOVNO r16, r16/m16: 66 0F 41 /r
			#  CMOVNP r16, r16/m16: 66 0F 4B /r
			#  CMOVNS r16, r16/m16: 66 0F 49 /r
			#  CMOVNZ r16, r16/m16: 66 0F 45 /r
			#   CMOVO r16, r16/m16: 66 0F 40 /r
			#   CMOVP r16, r16/m16: 66 0F 4A /r
			#  CMOVPE r16, r16/m16: 66 0F 4A /r
			#  CMOVPO r16, r16/m16: 66 0F 4B /r
			#   CMOVS r16, r16/m16: 66 0F 48 /r
			#   CMOVZ r16, r16/m16: 66 0F 44 /r
			self.destination = destination
			self.source = source
			self.size = 1 + 3 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		input_registers_list = [self.destination]
		input_registers_list.extend(self.source.get_registers_list)
		return input_registers_list

	def get_output_registers_list(self):
		return [self.destination.register]

class SetInstruction(Instruction):
	def __init__(self, name, destination):
		super(SetInstruction, self).__init__(name)
		allowed_instructions = [ 'SETA',  'SETAE',  'SETB',  'SETBE',  'SETC',  'SETE',  'SETG',  'SETGE',  'SETL',  'SETLE',  'SETO',  'SETP',  'SETPO',  'SETS',  'SETZ',
								'SETNA', 'SETNAE', 'SETNB', 'SETNBE', 'SETNC', 'SETNE', 'SETNG', 'SETNGE', 'SETNL', 'SETNLE', 'SETNO', 'SETNP', 'SETNPO', 'SETNS', 'SETNZ']
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register8() or destination.is_memory_address8():
			#   SETA r32, r32/m32: 0F 97 /r
			#  SETAE r32, r32/m32: 0F 93 /r
			#   SETB r32, r32/m32: 0F 92 /r
			#  SETBE r32, r32/m32: 0F 96 /r
			#   SETC r32, r32/m32: 0F 92 /r
			#   SETE r32, r32/m32: 0F 94 /r
			#   SETG r32, r32/m32: 0F 9F /r
			#  SETGE r32, r32/m32: 0F 9D /r
			#   SETL r32, r32/m32: 0F 9C /r
			#  SETLE r32, r32/m32: 0F 9E /r
			#  SETNA r32, r32/m32: 0F 96 /r
			# SETNAE r32, r32/m32: 0F 92 /r
			#  SETNB r32, r32/m32: 0F 93 /r
			# SETNBE r32, r32/m32: 0F 97 /r
			#  SETNC r32, r32/m32: 0F 93 /r
			#  SETNE r32, r32/m32: 0F 95 /r
			#  SETNG r32, r32/m32: 0F 9E /r
			# SETNGE r32, r32/m32: 0F 9C /r
			#  SETNL r32, r32/m32: 0F 9D /r
			# SETNLE r32, r32/m32: 0F 9F /r
			#  SETNO r32, r32/m32: 0F 91 /r
			#  SETNP r32, r32/m32: 0F 9B /r
			#  SETNS r32, r32/m32: 0F 99 /r
			#  SETNZ r32, r32/m32: 0F 95 /r
			#   SETO r32, r32/m32: 0F 90 /r
			#   SETP r32, r32/m32: 0F 9A /r
			#  SETPE r32, r32/m32: 0F 9A /r
			#  SETPO r32, r32/m32: 0F 9B /r
			#   SETS r32, r32/m32: 0F 98 /r
			#   SETZ r32, r32/m32: 0F 94 /r
			self.destination = destination
			self.size = 3 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}".format(self.name, self.destination)

	def get_input_registers_list(self):
		if self.destination.is_general_purpose_register8():
			return list()
		else:
			return self.destination.get_register_list()

	def get_output_registers_list(self):
		if self.destination.is_general_purpose_register8():
			return [self.destination.register]
		else:
			return list()

class SseMovInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		allowed_instructions = [ 'MOVAPS', 'MOVUPS', 'MOVAPD', 'MOVUPD', 'MOVDQA', 'MOVDQU', 'LDDQU' ]
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		is_ps = name in ['MOVAPS', 'MOVUPS']
		if is_ps:
			super(SseMovInstruction, self).__init__(name, destination, source, 'SSE')
		else:
			super(SseMovInstruction, self).__init__(name, destination, source, 'SSE2')
		if name == 'LDDQU':
			if destination.is_sse_register() and source.is_memory_address128():
				# LDDQU xmm, m128: F2 0F F0 /r
				self.size = 1 + 3 + source.get_modrm_extra_length()
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))
		else:
			if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
				# MOVAPS xmm, xmm/m128: 0F 28 /r
				# MOVUPS xmm, xmm/m128: 0F 10 /r
				# MOVAPD xmm, xmm/m128: 66 0F 28 /r
				# MOVUPD xmm, xmm/m128: 66 0F 10 /r
				# MOVDQA xmm, xmm/m128: 66 0F 6F /r
				# MOVDQU xmm, xmm/m128: F3 0F 6F /r
				if is_ps:
					self.size = 3 + source.get_modrm_extra_length()
				else:
					self.size = 1 + 3 + source.get_modrm_extra_length()
			elif (destination.is_sse_register() or destination.is_memory_address128()) and source.is_sse_register():
				# MOVAPS xmm/m128, xmm: 0F 29 /r
				# MOVUPS xmm/m128, xmm: 0F 11 /r
				# MOVAPD xmm/m128, xmm: 66 0F 29 /r
				# MOVUPD xmm/m128, xmm: 66 0F 11 /r
				# MOVDQA xmm/m128, xmm: 66 0F 7F /r
				# MOVDQU xmm/m128, xmm: F3 0F 7F /r
				if is_ps:
					self.size = 3 + destination.get_modrm_extra_length()
				else:
					self.size = 1 + 3 + destination.get_modrm_extra_length()
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		input_registers_list = list()
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		input_registers_list.extend(self.source.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_sse_register():
			return [self.destination.register]
		else:
			return list()

class MxcsrControlInstruction(Instruction):
	def __init__(self, name, operand):
		allowed_instructions = ['LDMXCSR', 'STMXCSR']
		if name in allowed_instructions:
			super(MxcsrControlInstruction, self).__init__(name, 'SSE')
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if operand.is_memory_address32():
			# LDMXCSR m32: 0F AE /2
			# STMXCSR m32: 0F AE /3
			self.operand = operand
			self.size = 3 + operand.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}".format(self.name, self.operand)

	def get_input_registers_list(self):
		return self.operand.get_registers_list()

	def get_output_registers_list(self):
		return list()

class SseScalarFloatingPointMovInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		allowed_instructions = [ 'MOVSS', 'MOVSD' ]
		if not name in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if name == 'MOVSS':
			super(SseScalarFloatingPointMovInstruction, self).__init__(name, destination, source, 'SSE')
		else:
			super(SseScalarFloatingPointMovInstruction, self).__init__(name, destination, source, 'SSE2')
		if name == 'MOVSS' and (destination.is_sse_register() or destination.is_memory_address32()) and source.is_sse_register():
			# MOVSS xmm/m32, xmm: F3 0F 11 /r
			self.size = 4 + destination.get_modrm_extra_length()
		elif name == 'MOVSS' and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address32()):
			# MOVSS xmm, xmm/m32: F3 0F 10 /r
			self.size = 4 + source.get_modrm_extra_length()
		elif name == 'MOVSD' and (destination.is_sse_register() or destination.is_memory_address64()) and source.is_sse_register():
			# MOVSD xmm/m64, xmm: F2 0F 11 /r
			self.size = 4 + destination.get_modrm_extra_length()
		elif name == 'MOVSD' and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()):
			# MOVSD xmm, xmm/m64: F2 0F 10 /r
			self.size = 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.destination.is_sse_register():
			return [self.destination.register]
		else:
			return list()

class SseFloatingPointBinaryInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		sse_scalar_instructions = [ 'ADDSS', 'SUBSS', 'MULSS', 'DIVSS', 'MINSS', 'MAXSS',
									'CMPEQSS',  'CMPLTSS',  'CMPLESS',  'CMPUNORDSS', 
									'CMPNEQSS', 'CMPNLTSS', 'CMPNLESS', 'CMPORDSS']
		sse_vector_instructions = [ 'ADDPS', 'SUBPS', 'MULPS', 'DIVPS', 'MINPS', 'MAXPS',
									'ANDPS', 'ANDNPS', 'ORPS', 'XORPS',  'UNPCKLPS', 'UNPCKHPS',
									'CMPEQPS',  'CMPLTPS',  'CMPLEPS',  'CMPUNORDPS', 
									'CMPNEQPS', 'CMPNLTPS', 'CMPNLEPS', 'CMPORDPS']
		sse_instructions = sse_scalar_instructions + sse_vector_instructions
		sse2_scalar_instructions = ['ADDSD', 'SUBSD', 'MULSD', 'DIVSD', 'MINSD', 'MAXSD',
									'CMPEQSD',  'CMPLTSD',  'CMPLESD',  'CMPUNORDSD', 
									'CMPNEQSD', 'CMPNLTSD', 'CMPNLESD', 'CMPORDSD']
		sse2_vector_instructions = ['ADDPD', 'SUBPD', 'MULPD', 'DIVPD', 'MINPD', 'MAXPD',
									'ANDPD', 'ANDNPD', 'ORPD', 'XORPD',  'UNPCKLPD', 'UNPCKHPD',
									'CMPEQPD',  'CMPLTPD',  'CMPLEPD',  'CMPUNORDPD', 
									'CMPNEQPD', 'CMPNLTPD', 'CMPNLEPD', 'CMPORDPD']
		sse3_vector_instructions = ['ADDSUBPS', 'ADDSUBPD', 'HADDPS', 'HADDPD', 'HSUBPS', 'HSUBPD']
		sse2_instructions =  sse2_scalar_instructions + sse2_vector_instructions
		vector_instructions = sse_vector_instructions + sse2_vector_instructions + sse3_vector_instructions
		if name in sse_instructions:
			super(SseFloatingPointBinaryInstruction, self).__init__(name, destination, source, 'SSE')
		elif name in sse2_instructions:
			super(SseFloatingPointBinaryInstruction, self).__init__(name, destination, source, 'SSE2')
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(sse_instructions + sse2_instructions))
		if name in vector_instructions and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# ADDPS xmm, xmm/m128: 0F 58 /r
			# ADDPD xmm, xmm/m128: 66 0F 58 /r

			# SUBPS xmm, xmm/m128: 0F 5C /r
			# SUBPD xmm, xmm/m128: 66 0F 5C /r

			# MULPS xmm, xmm/m128: 0F 59 /r
			# MULPD xmm, xmm/m128: 66 0F 59 /r

			# DIVPS xmm, xmm/m128: 0F 5E /r
			# DIVPD xmm, xmm/m128: 66 0F 5E /r

			# CMPPS xmm, xmm/m128: 0F C2 /r
			# CMPPD xmm, xmm/m128: 66 0F C2 /r

			# MINPS xmm, xmm/m128: 0F 5D /r
			# MINPD xmm, xmm/m128: 66 0F 5D /r

			# MAXPS xmm, xmm/m128: 0F 5F /r
			# MAXPD xmm, xmm/m128: 66 0F 5F /r

			# ANDPS xmm, xmm/m128: 0F 54 /r
			# ANDPD xmm, xmm/m128: 66 0F 54 /r

			# ANDNPS xmm, xmm/m128: 0F 55 /r
			# ANDNPD xmm, xmm/m128: 66 0F 55 /r

			# ORPS xmm, xmm/m128: 0F 56 /r
			# ORPD xmm, xmm/m128: 66 0F 56 /r

			# XORPS xmm, xmm/m128: 0F 57 /r
			# XORPD xmm, xmm/m128: 66 0F 57 /r

			# UNPCKLPS xmm, xmm/m128: 0F 14 /r
			# UNPCKLPD xmm, xmm/m128: 66 0F 14 /r

			# UNPCKHPS xmm, xmm/m128: 0F 15 /r
			# UNPCKHPD xmm, xmm/m128: 66 0F 15 /r

			# ADDSUBPS xmm, xmm/m128: F2 0F D0 /r
			# ADDSUBPD xmm, xmm/m128: 66 0F D0 /r
			#   HADDPS xmm, xmm/m128: F2 0F 7C /r
			#   HADDPD xmm, xmm/m128: 66 0F 7C /r
			#   HSUBPS xmm, xmm/m128: F2 0F 7D /r
			#   HSUBPD xmm, xmm/m128: 66 0F 7D /r

			if name in sse_vector_instructions:
				self.size = 3 + source.get_modrm_extra_length()
			elif name in sse2_vector_instructions:
				self.size = 4 + source.get_modrm_extra_length()
			elif name in sse3_vector_instructions:
				self.size = 4 + source.get_modrm_extra_length()
		elif name in sse_scalar_instructions and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address32()):
			# ADDSS xmm, xmm/m128: F3 0F 58 /r
			# SUBSS xmm, xmm/m128: F3 0F 5C /r
			# MULSS xmm, xmm/m128: F3 0F 59 /r
			# DIVSS xmm, xmm/m128: F3 0F 5E /r
			# CMPSS xmm, xmm/m128: F3 0F C2 /r
			# MINSS xmm, xmm/m128: F3 0F 5D /r
			# MAXSS xmm, xmm/m128: F3 0F 5F /r

			self.size = 4 + source.get_modrm_extra_length()
		elif name in sse2_scalar_instructions and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()):
			# ADDSD xmm, xmm/m128: F2 0F 58 /r
			# SUBSD xmm, xmm/m128: F2 0F 5C /r
			# MULSD xmm, xmm/m128: F2 0F 59 /r
			# DIVSD xmm, xmm/m128: F2 0F 5E /r
			# CMPSD xmm, xmm/m128: F2 0F C2 /r
			# MINSD xmm, xmm/m128: F2 0F 5D /r
			# MAXSD xmm, xmm/m128: F2 0F 5F /r

			self.size = 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		if self.name in [ 'XORPS', 'XORPD', 'ANDNPS', 'ANDNPD' ] and self.source == self.destination:
			return list()
		else:
			return self.source.get_registers_list() + self.destination.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

class SseIntegerBinaryInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		sse2_instructions = [ 'PADDB', 'PADDW', 'PADDD', 'PADDQ', 'PSUBB', 'PSUBW', 'PSUBD', 'PSUBQ',
							  'PADDSB', 'PADDSW', 'PADDUSB', 'PADDUSW',
							  'PSUBSB', 'PSUBSW', 'PSUBUSB', 'PSUBUSW',
							  'PAVGB', 'PAVGW', 'PMAXUB', 'PMAXSW', 'PMINUB', 'PMINSW', 'PSADBW'
							  'PAND', 'PANDN', 'POR', 'PXOR',
							  'PCMPEQB', 'PCMPEQW', 'PCMPEQD', 'PCMPGTB', 'PCMPGTW', 'PCMPGTD',
							  'PMULUDQ', 'PMULLW', 'PMULHW', 'PMULHUW', 'PMADDWD',
							  'PUNPCKLBW', 'PUNPCKHBW', 'PUNPCKLWD', 'PUNPCKHWD', 'PUNPCKLDQ', 'PUNPCKHDQ',
							  'PUNPCKLQDQ', 'PUNPCKHQDQ', 'PACKSSWB', 'PACKSSDW', 'PACKUSWB']
		ssse3_instructions = [ 'PSIGNB', 'PSIGNW', 'PSIGND', 'PABSB', 'PABSW', 'PABSD',
							   'PHADDW', 'PHADDD', 'PHSUBW', 'PHSUBD', 'PHADDSW', 'PHSUBSW',
							   'PSHUFB', 'PMULHRSW', 'PMADDUBSW']
		sse41_instructions = [ 'PCMPEQQ', 'PACKUSDW', 'PTEST',
							   'PMULLD', 'PMULDQ',
							   'PMAXSB', 'PMAXSD', 'PMAXUW', 'PMAXUD',
							   'PMINSB', 'PMINSD', 'PMINUW', 'PMINUD', 'PHMINPOSUW']
		sse42_instructions = [ 'PCMPGTQ' ]
		aes_instructions = [ 'AESIMC', 'AESENC', 'AESENCLAST', 'AESDEC', 'AESDECLAST' ]
		if name in sse2_instructions:
			super(SseIntegerBinaryInstruction, self).__init__(name, destination, source, 'SSE2')
		elif name in ssse3_instructions:
			super(SseIntegerBinaryInstruction, self).__init__(name, destination, source, 'SSSE3')
		elif name in sse41_instructions:
			super(SseIntegerBinaryInstruction, self).__init__(name, destination, source, 'SSE4.1')
		elif name in sse42_instructions:
			super(SseIntegerBinaryInstruction, self).__init__(name, destination, source, 'SSE4.2')
		elif name in aes_instructions:
			super(SseIntegerBinaryInstruction, self).__init__(name, destination, source, 'AES')
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(sse2_instructions + ssse3_instructions))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# PADDB xmm, xmm/m128: 66 0F FC /r
			# PADDW xmm, xmm/m128: 66 0F FD /r
			# PADDD xmm, xmm/m128: 66 0F FE /r
			# PADDQ xmm, xmm/m128: 66 0F D4 /r

			# PSUBB xmm, xmm/m128: 66 0F F8 /r
			# PSUBW xmm, xmm/m128: 66 0F F9 /r
			# PSUBD xmm, xmm/m128: 66 0F FA /r
			# PSUBQ xmm, xmm/m128: 66 0F FB /r

			#  PADDSB xmm, xmm/m128: 66 0F EC /r
			#  PADDSW xmm, xmm/m128: 66 0F ED /r
			# PADDUSB xmm, xmm/m128: 66 0F DC /r
			# PADDUSW xmm, xmm/m128: 66 0F DD /r

			#  PSUBSB xmm, xmm/m128: 66 0F E8 /r
			#  PSUBSW xmm, xmm/m128: 66 0F E9 /r
			# PSUBUSB xmm, xmm/m128: 66 0F D8 /r
			# PSUBUSW xmm, xmm/m128: 66 0F D9 /r

			#  PAVGB xmm, xmm/m128: 66 0F E0 /r
			#  PAVGW xmm, xmm/m128: 66 0F E3 /r
			# PMAXUB xmm, xmm/m128: 66 0F DE /r
			# PMAXSW xmm, xmm/m128: 66 0F EE /r
			# PMINUB xmm, xmm/m128: 66 0F DA /r
			# PMINSW xmm, xmm/m128: 66 0F EA /r

			#  PAND xmm, xmm/m128: 66 0F DB /r
			# PANDN xmm, xmm/m128: 66 0F DF /r
			#   POR xmm, xmm/m128: 66 0F EB /r
			#  PXOR xmm, xmm/m128: 66 0F EF /r

			# PCMPEQB xmm, xmm/m128: 66 0F 74 /r
			# PCMPEQW xmm, xmm/m128: 66 0F 75 /r
			# PCMPEQD xmm, xmm/m128: 66 0F 76 /r
			# PCMPGTB xmm, xmm/m128: 66 0F 64 /r
			# PCMPGTW xmm, xmm/m128: 66 0F 65 /r
			# PCMPGTD xmm, xmm/m128: 66 0F 66 /r

			# PMULUDQ xmm, xmm/m128: 66 0F F4 /r
			#  PMULLW xmm, xmm/m128: 66 0F D5 /r
			#  PMULHW xmm, xmm/m128: 66 0F E5 /r
			# PMULHUW xmm, xmm/m128: 66 0F E4 /r

			# PUNPCKLBW xmm, xmm/m128: 66 0F 60 /r
			# PUNPCKHBW xmm, xmm/m128: 66 0F 68 /r
			# PUNPCKLWD xmm, xmm/m128: 66 0F 61 /r
			# PUNPCKHWD xmm, xmm/m128: 66 0F 69 /r
			# PUNPCKLDQ xmm, xmm/m128: 66 0F 62 /r
			# PUNPCKHDQ xmm, xmm/m128: 66 0F 6A /r

			# PUNPCKLQDQ xmm, xmm/m128: 66 0F 6C /r
			# PUNPCKHQDQ xmm, xmm/m128: 66 0F 6D /r
			#   PACKSSWB xmm, xmm/m128: 66 0F 63 /r
			#   PACKSSDW xmm, xmm/m128: 66 0F 6B /r
			#   PACKUSWB xmm, xmm/m128: 66 0F 67 /r

			# PSIGNB xmm, xmm/m128: 66 0F 38 08 /r
			# PSIGNW xmm, xmm/m128: 66 0F 38 09 /r
			# PSIGND xmm, xmm/m128: 66 0F 38 0A /r
			#  PABSB xmm, xmm/m128: 66 0F 38 1C /r
			#  PABSW xmm, xmm/m128: 66 0F 38 1D /r
			#  PABSD xmm, xmm/m128: 66 0F 38 1E /r

			#  PHADDW xmm, xmm/m128: 66 0F 38 01 /r
			#  PHADDD xmm, xmm/m128: 66 0F 38 02 /r
			# PHADDSW xmm, xmm/m128: 66 0F 38 03 /r
			#  PHSUBW xmm, xmm/m128: 66 0F 38 05 /r
			#  PHSUBD xmm, xmm/m128: 66 0F 38 06 /r
			# PHSUBSW xmm, xmm/m128: 66 0F 38 07 /r

			#    PSHUFB xmm, xmm/m128: 66 0F 38 00 /r
			#  PMULHRSW xmm, xmm/m128: 66 0F 38 0B /r
			# PMADDUBSW xmm, xmm/m128: 66 0F 38 04 /r

			#   PCMPEQQ xmm, xmm/m128: 66 0F 38 29 /r
			#  PACKUSDW xmm, xmm/m128: 66 0F 38 2B /r
			#     PTEST xmm, xmm/m128: 66 0F 38 17 /r
			#    PMULLD xmm, xmm/m128: 66 0F 38 40 /r
			#    PMULDQ xmm, xmm/m128: 66 0F 38 28 /r

			# PMAXSB xmm, xmm/m128: 66 0F 38 3C /r
			# PMAXSD xmm, xmm/m128: 66 0F 38 3D /r
			# PMAXUW xmm, xmm/m128: 66 0F 38 3E /r
			# PMAXUD xmm, xmm/m128: 66 0F 38 3F /r

			#     PMINSB xmm, xmm/m128: 66 0F 38 38 /r
			#     PMINSD xmm, xmm/m128: 66 0F 38 39 /r
			#     PMINUW xmm, xmm/m128: 66 0F 38 3A /r
			#     PMINUD xmm, xmm/m128: 66 0F 38 3B /r
			# PHMINPOSUW xmm, xmm/m128: 66 0F 38 41 /r

			# PCMPGTQ xmm, xmm/m128: 66 0F 38 37 /r

			#     AESIMC xmm, xmm/m128: 66 0F 38 DB /r
			#     AESENC xmm, xmm/m128: 66 0F 38 DC /r
			# AESENCLAST xmm, xmm/m128: 66 0F 38 DD /r
			#     AESDEC xmm, xmm/m128: 66 0F 38 DE /r
			# AESDECLAST xmm, xmm/m128: 66 0F 38 DF /r

			if name in sse2_instructions:
				self.size = 4 + source.get_modrm_extra_length()
			else:
				self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

class MmxSseShiftInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		shift_instructions = ['PSLLW', 'PSLLD', 'PSLLQ',
		                      'PSRLW', 'PSRLD', 'PSRLQ',
		                      'PSRAW', 'PSRAD']
		if name in shift_instructions:
			super(SseShiftInstruction, self).__init__(name, destination, source, "SSE2")
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(shift_instructions))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# PSLLW xmm, xmm/m128: 66 0F F1 /r
			# PSLLD xmm, xmm/m128: 66 0F F2 /r
			# PSLLQ xmm, xmm/m128: 66 0F F3 /r
			# PSRLW xmm, xmm/m128: 66 0F D1 /r
			# PSRLD xmm, xmm/m128: 66 0F D2 /r
			# PSRLQ xmm, xmm/m128: 66 0F D3 /r
			# PSRAW xmm, xmm/m128: 66 0F E1 /r
			# PSRAD xmm, xmm/m128: 66 0F E2 /r
			self.size = 4 + source.get_modrm_extra_length(source)
		elif destination.is_sse_register() and source.is_int8():
			# PSLLW xmm, xmm/m128: 66 0F 71 /6 ib
			# PSLLD xmm, xmm/m128: 66 0F 72 /6 ib
			# PSLLQ xmm, xmm/m128: 66 0F 73 /6 ib
			# PSRLW xmm, xmm/m128: 66 0F 71 /2 ib
			# PSRLD xmm, xmm/m128: 66 0F 72 /2 ib
			# PSRLQ xmm, xmm/m128: 66 0F 73 /2 ib
			# PSRAW xmm, xmm/m128: 66 0F 71 /4 ib
			# PSRAD xmm, xmm/m128: 66 0F 72 /4 ib
			self.size = 4 + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

class SseOctowordShiftInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		shift_instructions = ['PSLLDQ', 'PSRLDQ']
		if name in shift_instructions:
			super(SseOctowordShiftInstruction, self).__init__(name, destination, source, "SSE2")
		else:
			raise ValueError('Instruction {0} is not one of the octoword shift instructions ({1})', name, ", ".join(shift_instructions))
		if destination.is_sse_register() and source.is_int8():
			# PSLLDQ xmm, imm8: 66 0F 73 /7 ib
			# PSRLDQ xmm, imm8: 66 0F 73 /3 ib
			self.size = 4 + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

class SseMovExtendInstruction(BinaryInstruction):
	def __init__(self, name, destination, source):
		m16_loads = [ 'PMOVSXBQ', 'PMOVZXBQ' ]
		m32_loads = [ 'PMOVSXBD', 'PMOVZXBD', 'PMOVSXWQ', 'PMOVZXWQ' ]
		m64_loads = [ 'PMOVSXBW', 'PMOVZXBW', 'PMOVSXWD', 'PMOVZXWD', 'PMOVSXDQ', 'PMOVZXDQ' ]
		mov_extend_instructions = m16_loads + m32_loads + m64_loads
		if name in mov_extend_instructions:
			super(SseMovExtendInstruction, self).__init__(name, destination, source, 'SSE4.1')
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(mov_extend_instructions))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address16()) and name in m16_loads:
			# PMOVSXBQ xmm, xmm/m16: 66 0F 38 22 /r
			# PMOVZXBQ xmm, xmm/m16: 66 0F 38 32 /r
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address32()) and name in m32_loads:
			# PMOVSXBD xmm, xmm/m32: 66 0F 38 21 /r
			# PMOVZXBD xmm, xmm/m32: 66 0F 38 31 /r
			# PMOVSXWQ xmm, xmm/m32: 66 0F 38 24 /r
			# PMOVZXWQ xmm, xmm/m32: 66 0F 38 34 /r
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()) and name in m64_loads:
			# PMOVSXBW xmm, xmm/m64: 66 0F 38 20 /r
			# PMOVZXBW xmm, xmm/m64: 66 0F 38 30 /r
			# PMOVSXWD xmm, xmm/m64: 66 0F 38 23 /r
			# PMOVZXWD xmm, xmm/m64: 66 0F 38 33 /r
			# PMOVSXDQ xmm, xmm/m64: 66 0F 38 25 /r
			# PMOVZXDQ xmm, xmm/m64: 66 0F 38 35 /r
			self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

class JmpInstruction(Instruction):
	def __init__(self, destination):
		super(JmpInstruction, self).__init__("JMP")
		if destination.is_label():
			self.destination = destination.label
			#   JA rel32: 0F 87 cd
			#  JAE rel32: 0F 83 cd
			#   JB rel32: 0F 82 cd
			#  JBE rel32: 0F 86 cd
			#   JC rel32: 0F 82 cd
			#   JE rel32: 0F 84 cd
			#   JZ rel32: 0F 84 cd
			self.size = 2 + 4
			self.is_visited = False
		else:
			raise TypeError('Only string names are accepted as destination labels')

	def __str__(self):
		return "{0} .{1}".format(self.name, self.destination)

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return list()

class PushInstruction(Instruction):
	def __init__(self, source):
		super(PushInstruction, self).__init__('PUSH')
		self.source = source
		if source.is_general_purpose_register32():
			self.size = 1
		else:
			raise ValueError('Invalid operand in instruction PUSH {0}'.format(source))

	def __str__(self):
		return "PUSH {0}".format(self.source)

	def get_input_registers_list(self):
		input_registers_list = [esp]
		input_registers_list.extend(self.source.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		return [esp]

class PopInstruction(Instruction):
	def __init__(self, destination):
		super(PopInstruction, self).__init__('POP')
		self.destination = destination
		if destination.is_general_purpose_register32():
			self.size = 1
		else:
			raise ValueError('Invalid operand in instruction POP {0}'.format(destination))

	def __str__(self):
		return "POP {0}".format(self.destination)

	def get_input_registers_list(self):
		input_registers_list = [esp]
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		output_registers_list = [esp]
		if self.destination.is_register():
			output_registers_list.append(self.destination.register)
		return output_registers_list

class RetInstruction(Instruction):
	def __init__(self, frame_size):
		super(RetInstruction, self).__init__('RET')
		if not frame_size.is_none and not frame_size.is_uint16():
			raise ValueError('Invalid operand in instruction RET {0}'.format(frame_size))
		if frame_size.is_none():
			self.immediate = 0
		else:
			self.immediate = frame_size.immediate
		if self.immediate == 0:
			self.size = 1
		else:
			self.size = 3

	def __str__(self):
		if self.immediate == 0:
			return "RET"
		else:
			return "RET {0}".format(self.immediate)

	def get_input_registers_list(self):
		return [esp]

	def get_output_registers_list(self):
		return [esp]

class ReturnInstruction(QuasiInstruction):
	def __init__(self, return_value = None):
		super(ReturnInstruction, self).__init__('RETURN')
		if return_value is None:
			self.return_value = None
		elif return_value.is_int32():
			self.return_value = return_value.immediate
		else:
			raise ValueError('Return value is not a 32-bit integer')

	def to_instruction_list(self):
		instruction_list = list()
		if self.return_value is None:
			pass
		if self.return_value == 0:
			instruction_list.append(ArithmeticInstruction('XOR', Operand(eax), Operand(eax)))
		else:
			instruction_list.append(MovInstruction(Operand(eax), Operand(self.return_value)))
		instruction_list.append(RetInstruction(Operand(None)))
		return instruction_list

	def get_input_registers_list(self):
		return [esp]

	def get_output_registers_list(self):
		return [esp]

def LABEL(name):
	current_function.add_instruction(Label(name))

def ALIGN(alignment):
	current_function.add_instruction(AlignQuasiInstruction(alignment))

def RETURN(return_value = None):
	current_function.add_instruction(ReturnInstruction(Operand(return_value)))

class LOAD:
	@staticmethod
	def CONSTANT(destination, source):
		current_function.add_instruction(LoadConstantPseudoInstruction(Operand(destination), Operand(source)))

	@staticmethod
	def PARAMETER(destination, source):
		current_function.add_instruction(LoadParameterPseudoInstruction(Operand(destination), source))

def ADD(destination, source):
	current_function.add_instruction(ArithmeticInstruction('ADD', Operand(destination), Operand(source)))

def ADC(destination, source):
	current_function.add_instruction(ArithmeticInstruction('ADC', Operand(destination), Operand(source)))

def SUB(destination, source):
	current_function.add_instruction(ArithmeticInstruction('SUB', Operand(destination), Operand(source)))

def SBB(destination, source):
	current_function.add_instruction(ArithmeticInstruction('SBB', Operand(destination), Operand(source)))

def CMP(destination, source):
	current_function.add_instruction(ArithmeticInstruction('CMP', Operand(destination), Operand(source)))

def AND(destination, source):
	current_function.add_instruction(ArithmeticInstruction('AND', Operand(destination), Operand(source)))

def OR(destination, source):
	current_function.add_instruction(ArithmeticInstruction('OR', Operand(destination), Operand(source)))

def XOR(destination, source):
	current_function.add_instruction(ArithmeticInstruction('XOR', Operand(destination), Operand(source)))

def TEST(destination, source):
	current_function.add_instruction(ArithmeticInstruction('TEST', Operand(destination), Operand(source)))

def SHL(destination, source):
	current_function.add_instruction(ShiftInstruction('SHL', Operand(destination), Operand(source)))

def SHR(destination, source):
	current_function.add_instruction(ShiftInstruction('SHR', Operand(destination), Operand(source)))

def SAR(destination, source):
	current_function.add_instruction(ShiftInstruction('SAR', Operand(destination), Operand(source)))

def ROL(destination, source):
	current_function.add_instruction(ShiftInstruction('ROL', Operand(destination), Operand(source)))

def ROR(destination, source):
	current_function.add_instruction(ShiftInstruction('ROR', Operand(destination), Operand(source)))

def RCL(destination, source):
	current_function.add_instruction(ShiftInstruction('RCL', Operand(destination), Operand(source)))

def RCR(destination, source):
	current_function.add_instruction(ShiftInstruction('RCR', Operand(destination), Operand(source)))

def BT(destination, source):
	current_function.add_instruction(BitTestInstruction('BT', Operand(destination), Operand(source)))

def BTS(destination, source):
	current_function.add_instruction(BitTestInstruction('BTS', Operand(destination), Operand(source)))

def BTR(destination, source):
	current_function.add_instruction(BitTestInstruction('BTR', Operand(destination), Operand(source)))

def BTC(destination, source):
	current_function.add_instruction(BitTestInstruction('BTC', Operand(destination), Operand(source)))

def IMUL(destination = None, source = None, immediate = None):
	current_function.add_instruction(ImulInstruction(Operand(destination), Operand(source), Operand(immediate)))

def MUL(source):
	current_function.add_instruction(MulInstruction(Operand(source)))

def RET(immediate = None):
	current_function.add_instruction(RetInstruction(Operand(immediate)))

def MOV(destination, source):
	current_function.add_instruction(MovInstruction(Operand(destination), Operand(source)))

def MOVZX(destination, source):
	current_function.add_instruction(MoveExtendInstruction('MOVZX', Operand(destination), Operand(source)))

def MOVSX(destination, source):
	current_function.add_instruction(MoveExtendInstruction('MOVSX', Operand(destination), Operand(source)))

def PUSH(source):
	current_function.add_instruction(PushInstruction(Operand(source)))

def POP(source):
	current_function.add_instruction(PopInstruction(Operand(source)))

def CMOVA(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVAE', Operand(destination), Operand(source)))

def CMOVAE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVAE', Operand(destination), Operand(source)))

def CMOVB(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVB', Operand(destination), Operand(source)))

def CMOVBE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVBE', Operand(destination), Operand(source)))

def CMOVC(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVC', Operand(destination), Operand(source)))

def CMOVE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVE', Operand(destination), Operand(source)))

def CMOVG(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVG', Operand(destination), Operand(source)))

def CMOVGE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVGE', Operand(destination), Operand(source)))

def CMOVL(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVL', Operand(destination), Operand(source)))

def CMOVLE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVLE', Operand(destination), Operand(source)))

def CMOVO(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVO', Operand(destination), Operand(source)))

def CMOVP(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVP', Operand(destination), Operand(source)))

def CMOVPO(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVPO', Operand(destination), Operand(source)))

def CMOVS(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVS', Operand(destination), Operand(source)))

def CMOVS(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVS', Operand(destination), Operand(source)))

def CMOVZ(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVZ', Operand(destination), Operand(source)))

def CMOVNA(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNA', Operand(destination), Operand(source)))

def CMOVNAE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNAE', Operand(destination), Operand(source)))

def CMOVNB(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNB', Operand(destination), Operand(source)))

def CMOVNBE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNBE', Operand(destination), Operand(source)))

def CMOVNC(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNC', Operand(destination), Operand(source)))

def CMOVNE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNE', Operand(destination), Operand(source)))

def CMOVNG(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNG', Operand(destination), Operand(source)))

def CMOVNGE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNGE', Operand(destination), Operand(source)))

def CMOVNL(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNL', Operand(destination), Operand(source)))

def CMOVNLE(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNLE', Operand(destination), Operand(source)))

def CMOVNO(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNO', Operand(destination), Operand(source)))

def CMOVNP(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNP', Operand(destination), Operand(source)))

def CMOVNPO(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNPO', Operand(destination), Operand(source)))

def CMOVNS(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNS', Operand(destination), Operand(source)))

def CMOVNS(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNS', Operand(destination), Operand(source)))

def CMOVNZ(destination, source):
	current_function.add_instruction(CmovInstruction('CMOVNZ', Operand(destination), Operand(source)))

def SETA(destination):
	current_function.add_instruction(SetInstruction('SETAE', Operand(destination)))

def SETAE(destination):
	current_function.add_instruction(SetInstruction('SETAE', Operand(destination)))

def SETB(destination):
	current_function.add_instruction(SetInstruction('SETB', Operand(destination)))

def SETBE(destination):
	current_function.add_instruction(SetInstruction('SETBE', Operand(destination)))

def SETC(destination):
	current_function.add_instruction(SetInstruction('SETC', Operand(destination)))

def SETE(destination):
	current_function.add_instruction(SetInstruction('SETE', Operand(destination)))

def SETG(destination):
	current_function.add_instruction(SetInstruction('SETG', Operand(destination)))

def SETGE(destination):
	current_function.add_instruction(SetInstruction('SETGE', Operand(destination)))

def SETL(destination):
	current_function.add_instruction(SetInstruction('SETL', Operand(destination)))

def SETLE(destination):
	current_function.add_instruction(SetInstruction('SETLE', Operand(destination)))

def SETO(destination):
	current_function.add_instruction(SetInstruction('SETO', Operand(destination)))

def SETP(destination):
	current_function.add_instruction(SetInstruction('SETP', Operand(destination)))

def SETPO(destination):
	current_function.add_instruction(SetInstruction('SETPO', Operand(destination)))

def SETS(destination):
	current_function.add_instruction(SetInstruction('SETS', Operand(destination)))

def SETS(destination):
	current_function.add_instruction(SetInstruction('SETS', Operand(destination)))

def SETZ(destination):
	current_function.add_instruction(SetInstruction('SETZ', Operand(destination)))

def SETNA(destination):
	current_function.add_instruction(SetInstruction('SETNA', Operand(destination)))

def SETNAE(destination):
	current_function.add_instruction(SetInstruction('SETNAE', Operand(destination)))

def SETNB(destination):
	current_function.add_instruction(SetInstruction('SETNB', Operand(destination)))

def SETNBE(destination):
	current_function.add_instruction(SetInstruction('SETNBE', Operand(destination)))

def SETNC(destination):
	current_function.add_instruction(SetInstruction('SETNC', Operand(destination)))

def SETNE(destination):
	current_function.add_instruction(SetInstruction('SETNE', Operand(destination)))

def SETNG(destination):
	current_function.add_instruction(SetInstruction('SETNG', Operand(destination)))

def SETNGE(destination):
	current_function.add_instruction(SetInstruction('SETNGE', Operand(destination)))

def SETNL(destination):
	current_function.add_instruction(SetInstruction('SETNL', Operand(destination)))

def SETNLE(destination):
	current_function.add_instruction(SetInstruction('SETNLE', Operand(destination)))

def SETNO(destination):
	current_function.add_instruction(SetInstruction('SETNO', Operand(destination)))

def SETNP(destination):
	current_function.add_instruction(SetInstruction('SETNP', Operand(destination)))

def SETNPO(destination):
	current_function.add_instruction(SetInstruction('SETNPO', Operand(destination)))

def SETNS(destination):
	current_function.add_instruction(SetInstruction('SETNS', Operand(destination)))

def SETNS(destination):
	current_function.add_instruction(SetInstruction('SETNS', Operand(destination)))

def SETNZ(destination):
	current_function.add_instruction(SetInstruction('SETNZ', Operand(destination)))

def JA(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JA', Operand(destination)))

def JAE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JAE', Operand(destination)))

def JB(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JB', Operand(destination)))

def JBE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JBE', Operand(destination)))

def JC(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JC', Operand(destination)))

def JE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JE', Operand(destination)))

def JG(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JG', Operand(destination)))

def JGE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JGE', Operand(destination)))

def JL(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JL', Operand(destination)))

def JLE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JLE', Operand(destination)))

def JO(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JO', Operand(destination)))

def JP(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JP', Operand(destination)))

def JPO(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JPO', Operand(destination)))

def JS(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JS', Operand(destination)))

def JZ(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JZ', Operand(destination)))

def JNA(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNA', Operand(destination)))

def JNAE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNAE', Operand(destination)))

def JNB(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNB', Operand(destination)))

def JNBE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNBE', Operand(destination)))

def JNC(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNC', Operand(destination)))

def JNE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNE', Operand(destination)))

def JNG(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNG', Operand(destination)))

def JNGE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNGE', Operand(destination)))

def JNL(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNL', Operand(destination)))

def JNLE(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNLE', Operand(destination)))

def JNO(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNO', Operand(destination)))

def JNP(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNP', Operand(destination)))

def JNPO(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNPO', Operand(destination)))

def JNS(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNS', Operand(destination)))

def JNZ(destination):
	current_function.add_instruction(ConditionalJumpInstruction('JNZ', Operand(destination)))

def JMP(destination):
	current_function.add_instruction(JmpInstruction(Operand(destination)))

def MOVAPS(destination, source):
	current_function.add_instruction(SseMovInstruction('MOVAPS', Operand(destination), Operand(source)))

def MOVUPS(destination, source):
	current_function.add_instruction(SseMovInstruction('MOVUPS', Operand(destination), Operand(source)))

def MOVAPD(destination, source):
	current_function.add_instruction(SseMovInstruction('MOVAPD', Operand(destination), Operand(source)))

def MOVUPD(destination, source):
	current_function.add_instruction(SseMovInstruction('MOVUPD', Operand(destination), Operand(source)))

def MOVDQA(destination, source):
	current_function.add_instruction(SseMovInstruction('MOVDQA', Operand(destination), Operand(source)))

def MOVDQU(destination, source):
	current_function.add_instruction(SseMovInstruction('MOVDQU', Operand(destination), Operand(source)))

def MOVSS(destination, source):
	current_function.add_instruction(SseScalarFloatingPointMovInstruction('MOVSS', Operand(destination), Operand(source)))

def MOVSD(destination, source):
	current_function.add_instruction(SseScalarFloatingPointMovInstruction('MOVSD', Operand(destination), Operand(source)))

def ADDSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ADDSS', Operand(destination), Operand(source)))

def ADDPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ADDPS', Operand(destination), Operand(source)))

def ADDSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ADDSD', Operand(destination), Operand(source)))

def ADDPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ADDPD', Operand(destination), Operand(source)))

def SUBSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('SUBSS', Operand(destination), Operand(source)))

def SUBPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('SUBPS', Operand(destination), Operand(source)))

def SUBSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('SUBSD', Operand(destination), Operand(source)))

def SUBPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('SUBPD', Operand(destination), Operand(source)))

def MULSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MULSS', Operand(destination), Operand(source)))

def MULPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MULPS', Operand(destination), Operand(source)))

def MULSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MULSD', Operand(destination), Operand(source)))

def MULPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MULPD', Operand(destination), Operand(source)))

def DIVSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('DIVSS', Operand(destination), Operand(source)))

def DIVPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('DIVPS', Operand(destination), Operand(source)))

def DIVSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('DIVSD', Operand(destination), Operand(source)))

def DIVPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('DIVPD', Operand(destination), Operand(source)))

def CMPSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('CMPSS', Operand(destination), Operand(source)))

def CMPPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('CMPPS', Operand(destination), Operand(source)))

def CMPSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('CMPSD', Operand(destination), Operand(source)))

def CMPPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('CMPPD', Operand(destination), Operand(source)))

def MINSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MINSS', Operand(destination), Operand(source)))

def MINPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MINPS', Operand(destination), Operand(source)))

def MINSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MINSD', Operand(destination), Operand(source)))

def MINPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MINPD', Operand(destination), Operand(source)))

def MAXSS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MAXSS', Operand(destination), Operand(source)))

def MAXPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MAXPS', Operand(destination), Operand(source)))

def MAXSD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MAXSD', Operand(destination), Operand(source)))

def MAXPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('MAXPD', Operand(destination), Operand(source)))

def ANDPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ANDPS', Operand(destination), Operand(source)))

def ANDPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ANDPD', Operand(destination), Operand(source)))

def ANDNPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ANDNPS', Operand(destination), Operand(source)))

def ANDNPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ANDNPD', Operand(destination), Operand(source)))

def ORPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ORPS', Operand(destination), Operand(source)))

def ORPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('ORPD', Operand(destination), Operand(source)))

def XORPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('XORPS', Operand(destination), Operand(source)))

def XORPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('XORPD', Operand(destination), Operand(source)))

def UNPCKLPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('UNPCKLPS', Operand(destination), Operand(source)))

def UNPCKLPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('UNPCKLPD', Operand(destination), Operand(source)))

def UNPCKHPS(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('UNPCKHPS', Operand(destination), Operand(source)))

def UNPCKHPD(destination, source):
	current_function.add_instruction(SseFloatingPointBinaryInstruction('UNPCKHPD', Operand(destination), Operand(source)))

def LDMXCSR(source):
	current_function.add_instruction(MxcsrControlInstruction('LDMXCSR', Operand(source)))

def STMXCSR(destination):
	current_function.add_instruction(MxcsrControlInstruction('STMXCSR', Operand(destination)))

def PADDB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDB', Operand(destination), Operand(source)))

def PADDW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDW', Operand(destination), Operand(source)))

def PADDD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDD', Operand(destination), Operand(source)))

def PADDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDQ', Operand(destination), Operand(source)))

def PSUBB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBB', Operand(destination), Operand(source)))

def PSUBW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBW', Operand(destination), Operand(source)))

def PSUBD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBD', Operand(destination), Operand(source)))

def PSUBQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBQ', Operand(destination), Operand(source)))

def PADDSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDSB', Operand(destination), Operand(source)))

def PADDSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDSW', Operand(destination), Operand(source)))

def PADDUSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDUSB', Operand(destination), Operand(source)))

def PADDUSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PADDUSW', Operand(destination), Operand(source)))

def PSUBSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBSB', Operand(destination), Operand(source)))

def PSUBSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBSW', Operand(destination), Operand(source)))

def PSUBUSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBUSB', Operand(destination), Operand(source)))

def PSUBUSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSUBUSW', Operand(destination), Operand(source)))

def PSLLW(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSLLW', Operand(destination), Operand(source)))

def PSLLD(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSLLD', Operand(destination), Operand(source)))

def PSLLQ(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSLLQ', Operand(destination), Operand(source)))

def PSRLW(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSRLW', Operand(destination), Operand(source)))

def PSRLD(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSRLD', Operand(destination), Operand(source)))

def PSRLQ(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSRLQ', Operand(destination), Operand(source)))

def PSRAW(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSRAW', Operand(destination), Operand(source)))

def PSRAD(destination, source):
	current_function.add_instruction(MmxSseShiftInstruction('PSRAD', Operand(destination), Operand(source)))

def PAVGB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PAVGB', Operand(destination), Operand(source)))

def PSLLDQ(destination, source):
	current_function.add_instruction(SseOctowordShiftInstruction('PSLLDQ', Operand(destination), Operand(source)))

def PSRLDQ(destination, source):
	current_function.add_instruction(SseOctowordShiftInstruction('PSRLDQ', Operand(destination), Operand(source)))

def PAVGW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PAVGW', Operand(destination), Operand(source)))

def PMAXUB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMAXUB', Operand(destination), Operand(source)))

def PMAXSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINUB', Operand(destination), Operand(source)))

def PMINUB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINUB', Operand(destination), Operand(source)))

def PMINSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINSW', Operand(destination), Operand(source)))

def PSADBW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSADBW', Operand(destination), Operand(source)))

def PAND(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PAND', Operand(destination), Operand(source)))

def PANDN(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PANDN', Operand(destination), Operand(source)))

def POR(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('POR', Operand(destination), Operand(source)))

def PXOR(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PXOR', Operand(destination), Operand(source)))

def PCMPEQB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPEQB', Operand(destination), Operand(source)))

def PCMPEQW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPEQW', Operand(destination), Operand(source)))

def PCMPEQD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPEQD', Operand(destination), Operand(source)))

def PCMPEQQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPEQQ', Operand(destination), Operand(source)))

def PCMPGTB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPGTB', Operand(destination), Operand(source)))

def PCMPGTW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPGTW', Operand(destination), Operand(source)))

def PCMPGTD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPGTD', Operand(destination), Operand(source)))

def PCMPGTQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PCMPGTQ', Operand(destination), Operand(source)))

def PMULLD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULLD', Operand(destination), Operand(source)))

def PMULDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULDQ', Operand(destination), Operand(source)))

def PMULUDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULUDQ', Operand(destination), Operand(source)))

def PMULLW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULLW', Operand(destination), Operand(source)))

def PMULHW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULHW', Operand(destination), Operand(source)))

def PMULHUW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULHUW', Operand(destination), Operand(source)))

def PMULHRSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMULHRSW', Operand(destination), Operand(source)))

def PMADDWD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMADDWD', Operand(destination), Operand(source)))

def PMADDUBSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMADDUBSW', Operand(destination), Operand(source)))

def PUNPCKLBW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKLBW', Operand(destination), Operand(source)))

def PUNPCKHBW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKHBW', Operand(destination), Operand(source)))

def PUNPCKLWD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKLWD', Operand(destination), Operand(source)))

def PUNPCKHWD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKHWD', Operand(destination), Operand(source)))

def PUNPCKLDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKLDQ', Operand(destination), Operand(source)))

def PUNPCKHDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKHDQ', Operand(destination), Operand(source)))

def PUNPCKLQDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKLQDQ', Operand(destination), Operand(source)))

def PUNPCKHQDQ(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PUNPCKHQDQ', Operand(destination), Operand(source)))

def PACKSSWB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PACKSSWB', Operand(destination), Operand(source)))

def PACKSSDW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PACKSSDW', Operand(destination), Operand(source)))

def PACKUSWB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PACKUSWB', Operand(destination), Operand(source)))

def PACKUSDW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PACKUSDW', Operand(destination), Operand(source)))

def PSIGNB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSIGNB', Operand(destination), Operand(source)))

def PSIGNW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSIGNW', Operand(destination), Operand(source)))

def PSIGND(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSIGND', Operand(destination), Operand(source)))

def PABSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PABSB', Operand(destination), Operand(source)))

def PABSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PABSW', Operand(destination), Operand(source)))

def PABSD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PABSD', Operand(destination), Operand(source)))

def PHADDW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHADDW', Operand(destination), Operand(source)))

def PHADDD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHADDD', Operand(destination), Operand(source)))

def PHSUBW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHSUBW', Operand(destination), Operand(source)))

def PHSUBD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHSUBD', Operand(destination), Operand(source)))

def PHADDSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHADDSW', Operand(destination), Operand(source)))

def PHSUBSW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHSUBSW', Operand(destination), Operand(source)))

def PSHUFB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PSHUFB', Operand(destination), Operand(source)))

def PTEST(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PTEST', Operand(destination), Operand(source)))

def PMAXSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMAXSB', Operand(destination), Operand(source)))

def PMAXSD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMAXSD', Operand(destination), Operand(source)))

def PMAXUW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMAXUW', Operand(destination), Operand(source)))

def PMAXUD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMAXUD', Operand(destination), Operand(source)))

def PMINSB(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINSB', Operand(destination), Operand(source)))

def PMINSD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINSD', Operand(destination), Operand(source)))

def PMINUW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINUW', Operand(destination), Operand(source)))

def PMINUD(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PMINUD', Operand(destination), Operand(source)))

def PHMINPOSUW(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('PHMINPOSUW', Operand(destination), Operand(source)))

def AESIMC(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('AESIMC', Operand(destination), Operand(source)))

def AESENC(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('AESENC', Operand(destination), Operand(source)))

def AESENCLAST(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('AESENCLAST', Operand(destination), Operand(source)))

def AESDEC(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('AESDEC', Operand(destination), Operand(source)))

def AESDECLAST(destination, source):
	current_function.add_instruction(SseIntegerBinaryInstruction('AESDECLAST', Operand(destination), Operand(source)))

def PMOVSXBW(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVSXBW', Operand(destination), Operand(source)))

def PMOVZXBW(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVZXBW', Operand(destination), Operand(source)))

def PMOVSXBD(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVSXBD', Operand(destination), Operand(source)))

def PMOVZXBD(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVZXBD', Operand(destination), Operand(source)))

def PMOVSXBQ(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVSXBQ', Operand(destination), Operand(source)))

def PMOVZXBQ(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVZXBQ', Operand(destination), Operand(source)))

def PMOVSXWD(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVSXWD', Operand(destination), Operand(source)))

def PMOVZXWD(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVZXWD', Operand(destination), Operand(source)))

def PMOVSXWQ(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVSXWQ', Operand(destination), Operand(source)))

def PMOVZXWQ(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVZXWQ', Operand(destination), Operand(source)))

def PMOVSXDQ(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVSXDQ', Operand(destination), Operand(source)))

def PMOVZXDQ(destination, source):
	current_function.add_instruction(SseMovExtendInstruction('PMOVZXDQ', Operand(destination), Operand(source)))

if __name__ == '__main__':
	import peachpy.codegen
	assembler = Assembler()
	assembler.begin_function("yepCore_Add_V32uV32u_V32u", ["xPointer", "yPointer", "sumPointer", "length"], "Nehalem", "x86")

	xPointer = esi
	yPointer = ebx
	sumPointer = edi
	length = ecx
	accumulator = eax
	temp = edx

	accumulator0 = xmm0
	accumulator1 = xmm1
	accumulator2 = xmm2
	accumulator3 = xmm3
	temp0 = xmm4
	temp1 = xmm5
	temp2 = xmm6
	temp3 = xmm7

	LOAD.PARAMETER( xPointer, "xPointer" )
	MOV( xPointer, [esp + 16 + 4] )
	MOV( yPointer, [esp + 16 + 8] )
	MOV( sumPointer, [esp + 16 + 12] )
	MOV( length, [esp + 16 + 16] )

	LOAD.CONSTANT( xmm0, Constant.uint64x2(0x10203040) )

	LABEL( "LOOP" )
	MOVUPD( accumulator0, [xPointer] )
	MOVUPD( accumulator1, [xPointer + 16] )
	MOVUPD( accumulator2, [xPointer + 32] )
	MOVUPD( accumulator3, [xPointer + 48] )

	MOVUPD( temp0, [yPointer] )
	MOVUPD( temp1, [yPointer + 16] )
	MOVUPD( temp2, [yPointer + 32] )
	MOVUPD( temp3, [yPointer + 48] )

	ADDPD( accumulator0, temp0 )
	ADDPD( accumulator1, temp1 )
	ADDPD( accumulator2, temp2 )
	ADDPD( accumulator3, temp3 )

	ADD( xPointer, 64 )
	ADD( yPointer, 64 )
	ADD( sumPointer, 64 )
	SUB( length, 8 )
	JNZ( "LOOP" )
	LABEL( "RETURN" )
	RETURN(0)

	assembler.end_function()
	print assembler