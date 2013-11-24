#
#        PEACH-Py: Portable Efficient Assembly Code-generator in Higher-level Python
#
# This file is part of Yeppp! library infrastructure and licensed under the New BSD license.
# See LICENSE.txt for the full text of the license.
#

from peachpy import Constant, ConstantBucket, RegisterAllocationError
import peachpy.codegen
import peachpy.c
import string
import inspect
import time

current_function = None
current_stream = None
supported_isa_extensions = ['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Div', 'Thumb', 'Thumb2',
                            'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'VFPVectorMode',
                            'XScale', 'WMMX', 'WMMX2', 'NEON', 'NEONHP', 'NEON2']

class Parameter(peachpy.c.Parameter):
	def __init__(self, parameter):
		if isinstance(parameter, peachpy.c.Parameter):
			super(Parameter, self).__init__(parameter.name, parameter.type)
			self.register = None
			self.stack_offset = None
		else:
			raise TypeError("Invalid parameter type {0}".format(type(parameter)))

class Microarchitecture(object):
	supported_microarchitectures = ['XScale',
	                                'ARM9', 'ARM11',
	                                'CortexA5', 'CortexA7', 'CortexA8', 'CortexA9', 'CortexA12', 'CortexA15', 
	                                'Scorpion', 'Krait',
	                                'Swift',
	                                'PJ1', 'PJ4']

	supported_isa_extensions = {'XScale'      : set(['V4', 'V5', 'V5E', 'Thumb', 'XScale', 'WMMX', 'WMMX2']),
	                            'ARM9'        : set(['V4', 'V5', 'V5E', 'Thumb']),
	                            'ARM11'       : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'Thumb', 'VFP', 'VFP2', 'VFPVectorMode']),
	                            'CortexA5'    : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'NEON', 'NEONHP', 'NEON2']),
	                            'CortexA7'    : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Div', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'NEON', 'NEONHP', 'NEON2']),
	                            'CortexA8'    : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'NEON']),
	                            'CortexA9'    : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'NEON', 'NEONHP']),
	                            'CortexA12'   : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Div', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'NEON', 'NEONHP', 'NEON2']),
	                            'CortexA15'   : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Div', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'NEON', 'NEONHP', 'NEON2']),
	                            'Scorpion'    : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'NEON', 'NEONHP']),
	                            'Krait'       : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Div', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'NEON', 'NEONHP', 'NEON2']),
	                            'Swift'       : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'V7MP', 'Div', 'Thumb', 'Thumb2', 'VFP', 'VFP2', 'VFP3', 'VFPd32', 'VFP3HP', 'VFP4', 'NEON', 'NEONHP', 'NEON2']),
	                            'PJ1'         : set(['V4', 'V5', 'V5E', 'Thumb']),
	                            'PJ4'         : set(['V4', 'V5', 'V5E', 'V6', 'V6K', 'V7', 'Thumb', 'Thumb2', 'XScale', 'VFP', 'VFP2', 'VFP3', 'WMMX', 'WMMX2']) }

	def __init__(self, name):
		super(Microarchitecture, self).__init__()
		if name in Microarchitecture.supported_microarchitectures:
			self.name = name
			self.supported_isa_extensions = Microarchitecture.supported_isa_extensions[self.name]
		else:
			raise ValueError('Unsupported microarchitecture {0}: only ({1}) microarchitectures are supported on this architecture'.format(name, ', '.join(Microarchitecture.supported_microarchitectures)))

	def __str__(self):
		descriptions = {'Unknown': 'Default',
		                'XScale': 'Intel XScale',
		                'ARM9': 'ARM9',
		                'ARM11': 'ARM11',
		                'CortexA5': 'ARM Cortex-A5',
		                'CortexA7': 'ARM Cortex-A7',
		                'CortexA8': 'ARM Cortex-A8',
		                'CortexA9': 'ARM Cortex-A9',
		                'CortexA12': 'ARM Cortex-A12',
		                'CortexA15': 'ARM Cortex-A15',
		                'Scorpion': 'Qualcomm Scorpion',
		                'Krait': 'Qualcomm Krait',
		                'Swift': 'Apple Swift',
		                'PJ1': 'Marvell PJ1',
		                'PJ4': 'Marvell PJ4'}
		return descriptions[self.get_name()]

	def get_name(self):
		return self.name

	def get_number(self):
		return Microarchitecture.supported_microarchitectures.index(self.get_name())

class Target:
	dependent_isa_extensions = {
	     'V4': ['V4'],
	     'V5': ['V5E', 'V6'],
	     'V6': ['V6K', 'V7'],
	     'V7': ['V7MP', 'Div'],
	     'Thumb': ['Thumb2'],
	     'VFP': ['VFP2'],
	     'VFP2': ['VFP3', 'VFPVectorMode'],
	     'VFP3': ['VFPd32', 'VFP3HP', 'VFP4'],
	     'VFPd32': ['NEON'],
	     'VFP3HP': ['VFP4', 'NEONHP'],
	     'VFP4': ['NEON2'],
	     'WMMX': ['WMMX2'],
	     'NEON': ['NEONHP'],
	     'NEONHP': ['VFP3HP', 'NEON2'],
	     'NEON2': ['VFP4']
	}
	
	@staticmethod
	def get_dependent_extensions(isa_extension):
		dependent_extensions = set([isa_extension])
		if isa_extension in Target.dependent_isa_extensions:
			for dependent_extension in Target.dependent_isa_extensions[isa_extension]:
				dependent_extensions.update(Target.get_dependent_extensions(dependent_extension))
		return dependent_extensions

	def __init__(self, microarchitecture, exclude_extensions = list()):
		if isinstance(microarchitecture, str):
			microarchitecture = Microarchitecture(microarchitecture)
		elif isinstance(microarchitecture, Microarchitecture):
			microarchitecture = microarchitecture
		else:
			raise TypeError("The microarchitecture must be either an instance of Microarchitecture class, or a valid name")
		self.microarchitecture = microarchitecture
		self.isa_extensions = set(Microarchitecture.supported_isa_extensions[self.microarchitecture.get_name()])
		for isa_extension in exclude_extensions:
			self.isa_extensions -= Target.get_dependent_extensions(isa_extension)

	@staticmethod
	def has_v5e():
		return 'V5E' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_v6():
		return 'V6' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_v6k_plus():
		return 'V6K' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_v7():
		return 'V7' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_v7mp():
		return 'V7MP' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_div():
		return 'Div' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vfp():
		return 'VFP' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vfp2():
		return 'VFP2' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vfp3():
		return 'VFP3' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vfpd32():
		return 'VFPd32' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vfp3hp():
		return 'VFP3HP' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vfp4():
		return 'VFP4' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_wmmx():
		return 'WMMX' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_wxmm2():
		return 'WMMX2' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_neon():
		return 'NEON' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_neonhp():
		return 'NEONHP' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_neon2():
		return 'NEON2' in Function.get_current().get_target().isa_extensions

class Assembler(peachpy.codegen.CodeGenerator):
	def __init__(self, abi):
		super(Assembler, self).__init__()
		if isinstance(abi, peachpy.c.ABI):
			if abi.get_name() in ["arm-softeabi", "arm-hardeabi"]:
				self.abi = abi
			else:
				raise ValueError('Unsupported abi {0}: only "arm-softeabi" and "arm-hardeabi" ABIs are supported on this architecture'.format(abi))
		else:
			raise TypeError('Wrong type of ABI object')
		self.functions = list()

	def __str__(self):
		return self.get_code()

	def find_functions(self, name):
		return [function for function in self.functions if function.name == name]

	def add_assembly_comment(self, lines, indent = None):
		for line in lines:
			self.add_line("@ " + line, indent)

class InstructionStream(object):
	def __init__(self):
		self.instructions = list()
		self.previous_stream = None

	def __enter__(self):
		global current_stream
		self.previous_stream = current_stream
		current_stream = self
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		global current_stream
		current_stream = self.previous_stream
		self.previous_stream = None

	def __iter__(self):
		return iter(self.instructions)

	def __len__(self):
		return len(self.instructions)
	
	def __getitem__(self, i):
		try:
			return self.instructions[i]
		except IndexError:
			return None

	def add_instruction(self, instruction):
		self.instructions.append(instruction)

	def issue(self, count = 1):
		for i in range(count):
			if self.instructions:
				current_stream.add_instruction(self.instructions.pop(0))
			
class Function(object):
	def __init__(self, assembler, name, arguments, microarchitecture, exclude_isa_extensions = list(), assembly_cache = dict(), collect_origin = False, dump_intermediate_assembly = False, check_only = False, report_generation = True, report_live_registers = False):
		super(Function, self).__init__()
		self.assembler = assembler
		self.name = name
		self.arguments = [peachpy.arm.Parameter(argument) for argument in arguments]
		self.target = Target(microarchitecture, exclude_isa_extensions)
		self.collect_origin = collect_origin
		self.dump_intermediate_assembly = dump_intermediate_assembly
		self.check_only = check_only
		self.report_generation = report_generation
		self.report_live_registers = report_live_registers
		self.ticks = None
		self.assembly_cache = assembly_cache

		# Determine parameters locations 
		if assembler.abi.name == 'arm-softeabi':
			argument_registers = (r0, r1, r2, r3)
			register_offset = 0
			stack_offset    = 0
			for argument in self.arguments:
				argument_size = argument.get_type().get_size(assembler.abi)
				if argument_size <= 4:
					if register_offset < 4:
						argument.register = argument_registers[register_offset]
						register_offset += 1
					else:
						argument.stack_offset = stack_offset
						stack_offset += 4
				elif argument_size == 8:
					if register_offset % 2 == 1:
						register_offset += 1
					if register_offset < 4:
						argument.register = (argument_registers[register_offset], argument_registers[register_offset + 1])
						register_offset += 2
					else:
						if stack_offset % 8 == 4:
							stack_offset += 4
						argument.stack_offset = stack_offset
						stack_offset += 8
				else:
					raise ValueError("Unsupported argument size {0}".format(argument_size))
		elif assembler.abi.name == 'arm-hardeabi':
			argument_registers = (r0, r1, r2, r3)
			register_offset = 0
			stack_offset    = 0
			for argument in self.arguments:
				argument_size = argument.get_type().get_size(assembler.abi)
				if argument_size <= 4:
					if register_offset < 4:
						argument.register = argument_registers[register_offset]
						register_offset += 1
					else:
						argument.stack_offset = stack_offset
						stack_offset += 4
				elif argument_size == 8:
					if register_offset % 2 == 1:
						register_offset += 1
					if register_offset < 4:
						argument.register = (argument_registers[register_offset], argument_registers[register_offset + 1])
						register_offset += 2
					else:
						if stack_offset % 8 == 4:
							stack_offset += 4
						argument.stack_offset = stack_offset
						stack_offset += 8
				else:
					raise ValueError("Unsupported argument size {0}".format(argument_size))
		else:
			raise ValueError("Unsupported assembler ABI") 

		self.symbol_name = "_" + name + "_" + microarchitecture
		self.abi = self.assembler.abi
		self.instructions = list()
		self.constants = list()
		self.stack_frame = StackFrame(self.abi)
		self.local_variables_count = 0
		self.virtual_registers_count = 0x40
		self.conflicting_registers = dict()
		self.allocation_options = dict()
		self.unallocated_registers = list()

	def __enter__(self):
		global current_function
		global current_stream

		if current_function is not None:
			raise ValueError('Function {0} was not detached'.format(current_function.name))
		if current_stream is not None:
			raise ValueError('Alternative instruction stream is active')
		current_function = self
		current_stream = self
		if self.report_generation:
			print "Generating function {0} for microarchitecture {1} and ABI {2}".format(self.name, self.target.microarchitecture, self.abi)
			print "\tParsing source",
			self.ticks = time.time()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		global current_stream
		import hashlib
		import copy
		
		current_stream = None
		if exc_type is None:
			try:
				self.generate_labels()
				self.decompose_instructions()
				self.reserve_registers()
				hash = hashlib.sha1()
				hash.update(str(self.abi) + "\n")
				for instruction in self.instructions:
					hash.update(str(instruction) + "\n")
				key = hash.hexdigest().upper()
				if key in self.assembly_cache:
					if self.report_generation:
						elapsed = time.time() - self.ticks
						print " (%2.2f secs)" % elapsed
						print "\tRestoring function from cache"
					self.instructions = copy.copy(self.assembly_cache[key])
					self.generate_constant_loads()
					self.optimize_instructions()
				else:
					if self.report_generation:
						elapsed = time.time() - self.ticks
						print " (%2.2f secs)" % elapsed
						print "\tRunning liveness analysis",
						self.ticks = time.time()
					self.determine_available_registers()
					self.determine_live_registers(exclude_parameter_loads = True)
			
					if self.dump_intermediate_assembly:
						with open('%s.S' % self.symbol_name, "w") as intermediate_assembly_file:  
							for instruction in self.instructions:
								if isinstance(instruction, Instruction):
									consumed_registers = ", ".join(sorted(map(str, list(instruction.get_input_registers_list()))))
									produced_registers = ", ".join(sorted(map(str, list(instruction.get_output_registers_list()))))
									available_registers = ", ".join(sorted(map(str, list(instruction.available_registers))))
									live_registers = ", ".join(sorted(map(str, list(instruction.live_registers))))
									intermediate_assembly_file.write(str(instruction) + "\n")
									intermediate_assembly_file.write("\tConsumed registers: " + consumed_registers + "\n")
									intermediate_assembly_file.write("\tProduced registers: " + produced_registers + "\n")
									intermediate_assembly_file.write("\tLive registers: " + live_registers + "\n")
									if instruction.line_number:
										intermediate_assembly_file.write("\tLine: " + str(instruction.line_number) + "\n")
									if instruction.source_code:
										intermediate_assembly_file.write("\tCode: " + instruction.source_code + "\n")
								else:
									intermediate_assembly_file.write(str(instruction) + "\n")
			
					if self.report_generation:
						elapsed = time.time() - self.ticks
						print " (%2.2f secs)" % elapsed
						print "\tRunning register allocation",
						self.ticks = time.time()
					self.check_live_registers()
					self.determine_register_relations()
					self.allocate_registers()
	
					if self.report_generation:
						elapsed = time.time() - self.ticks
						print " (%2.2f secs)" % elapsed
						print "\tGenerating code",
						self.ticks = time.time()
					self.remove_assume_statements()
					self.update_stack_frame()
					self.generate_parameter_loads()
					if self.report_live_registers:
						self.determine_live_registers()
					self.generate_prolog_and_epilog()

					self.assembly_cache[key] = copy.deepcopy(self.instructions)
					self.generate_constant_loads()
					self.optimize_instructions()
					if self.report_generation:
						elapsed = time.time() - self.ticks
						print " (%2.2f secs)" % elapsed
						self.ticks = time.time()
			finally:
				self.detach()
			self.assembler.functions.append(self)

			if not self.check_only:
				isa_extensions = set(self.get_isa_extensions())
		
				function_label = self.abi.function_prefix + self.symbol_name
				constants_label = self.symbol_name + "_constants"
				if len(self.constants) > 0:
					self.assembler.add_line('section .rodata.{0} progbits alloc noexec nowrite align={1}'.format(self.get_target().microarchitecture.get_name(), 32))
					self.assembler.add_line(constants_label + ':')
					data_declaration_map = {8: "DB", 16: "DW", 32: "DD", 64: "DQ", 128: "DO"}
					self.assembler.indent()
					need_alignment = False
					for constant_bucket in self.constants:
						if need_alignment:
							self.assembler.add_line("ALIGN {0}".format(constant_bucket.capacity))
						for constant in constant_bucket.constants:
							self.assembler.add_line(".{0}: {1} {2}".format(constant.label, data_declaration_map[constant.size], ", ".join([str(constant)] * constant.repeats)))
						need_alignment = not constant_bucket.is_full()
					self.assembler.dedent()
					self.assembler.add_line()
					self.assembler.add_line()
	
				self.assembler.add_line('.section .text.{0},"ax",%progbits'.format(self.get_target().microarchitecture.get_name()))
				self.assembler.add_line("BEGIN_ARM_FUNCTION " + function_label)
				self.assembler.indent()
				if 'Div' in isa_extensions:
					self.assembler.add_line(".cpu cortex-a15")
				elif 'V7MP' in isa_extensions:
					self.assembler.add_line('.cpu cortex-a9')
				elif 'V7' in isa_extensions:
					self.assembler.add_line('.arch armv7-a')
				elif 'V6K' in isa_extensions:
					self.assembler.add_line('.arch armv6zk')
				elif 'V6' in isa_extensions:
					self.assembler.add_line('.arch armv6')
				elif 'V5E' in isa_extensions:
					self.assembler.add_line('.arch armv5te')
				else:
					self.assembler.add_line('.arch armv5t')
				if 'NEON2' in isa_extensions or 'VFP4' in isa_extensions:
					self.assembler.add_line('.fpu neon-vfpv4')
				elif 'NEONHP' in isa_extensions or 'VFP3HP' in isa_extensions and 'NEON' in isa_extensions:
					self.assembler.add_line('.fpu neon-fp16')
				elif 'NEON' in isa_extensions:
					self.assembler.add_line('.fpu neon')
				elif 'VFP3HP' in isa_extensions and 'VFPd32' in isa_extensions:
					self.assembler.add_line('.fpu vfpv3-fp16')
				elif 'VFP3HP' in isa_extensions:
					self.assembler.add_line('.fpu vfpv3-d16-fp16')
				elif 'VFP3' in isa_extensions or 'VFPd32' in isa_extensions:
					self.assembler.add_line('.fpu vfpv3')
				elif 'VFP3' in isa_extensions or 'VFP2' in isa_extensions:
					self.assembler.add_line('.fpu vfpv3-d16')
				elif 'VFP' in isa_extensions:
					self.assembler.add_line('.fpu vfp')
				for instruction in self.instructions:
					if isinstance(instruction, BranchInstruction):
						self.assembler.add_line("{0} L{1}.{2}".format(instruction.name, self.symbol_name, instruction.operands[0].label))
					elif isinstance(instruction, Instruction):
						constant = instruction.get_constant()
						if constant is not None:
							constant.prefix = constants_label
						self.assembler.add_line(str(instruction))
					elif isinstance(instruction, LabelMark):
						self.assembler.add_line("L{0}.{1}:".format(self.symbol_name, instruction.name), indent = 0)
					else:
						self.assembler.add_line(str(instruction))
				self.assembler.dedent()
				self.assembler.add_line("END_ARM_FUNCTION " + function_label)
				self.assembler.add_line()
		else:
			self.detach()

	@staticmethod
	def get_current():
		global current_function
		if current_function is None:
			raise ValueError('No function is active')
		return current_function

	def detach(self):
		global current_function
		if current_function is None:
			raise ValueError('Trying to detach a function while no function is active')
		current_function = None
		current_stream = None
		return self

	def find_parameter(self, parameter):
		for argument in self.arguments:
			if argument.name == parameter.name:
				return argument
		return None

	def add_instruction(self, instruction):
		if instruction is None:
			return
		if isinstance(instruction, Instruction):
			isa_extension = instruction.get_isa_extension() 
			if isa_extension is not None:
				if isa_extension not in self.target.isa_extensions:
					raise ValueError("ISA extension {0} is not supported on {1}".format(isa_extension, self.target.microarchitecture))
			local_variable = instruction.get_local_variable()
			if local_variable is not None:
				self.stack_frame.add_variable(local_variable.get_root())
			self.stack_frame.preserve_registers(instruction.get_output_registers_list())
		self.instructions.append(instruction)

	def add_instructions(self, instructions):
		for instruction in instructions:
			self.add_instruction(instruction)

	def decompose_instructions(self):
		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, ReturnInstruction):
				new_instructions.extend(instruction.to_instruction_list())
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions
		
	def generate_prolog_and_epilog(self):
		prologue_instructions = self.stack_frame.generate_prologue()
		epilogue_instructions = self.stack_frame.generate_epilogue()
		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, LabelMark):
				new_instructions.append(instruction)
				if instruction.name == 'ENTRY':
					new_instructions.extend(prologue_instructions)
			elif isinstance(instruction, BranchExchangeInstruction):
				new_instructions.extend(epilogue_instructions)
				new_instructions.append(instruction)
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions

	def generate_labels(self):
		for instruction in self.instructions:
			if isinstance(instruction, LabelMark):
				if instruction.name == 'ENTRY':
					break
		else:
			self.instructions.insert(0, LabelMark(Operand("ENTRY")))

	def get_label_table(self):
		label_table = dict()
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, LabelMark):
				label_table[instruction.name] = index
		return label_table

	def find_entry_label(self):
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, LabelMark):
				if instruction.name == 'ENTRY':
					return index
		raise ValueError('Instruction stream does not contain the ENTRY label')

	def find_exit_points(self):
		ret_instructions = list()
		for index, instruction in enumerate(self.instructions):
			if isinstance(instruction, BranchExchangeInstruction):
				ret_instructions.append(index)
		return ret_instructions

	def determine_branches(self):
		label_table = self.get_label_table()
		for instruction in self.instructions:
			if isinstance(instruction, LabelMark):
				instruction.input_branches = set()

		for i, instruction in enumerate(self.instructions):
			if isinstance(instruction, BranchInstruction):
				target_label = instruction.operands[0].label
				target_index = label_table[target_label]
				self.instructions[target_index].input_branches.add(i)

	def reserve_registers(self):
		pass

	def determine_available_registers(self):
		processed_branches = set()
		label_table = self.get_label_table()

		def mark_available_registers(instructions, start, initial_available_registers):
			available_registers = set(initial_available_registers)
			for i in range(start, len(instructions)):
				instruction = instructions[i]
				if isinstance(instruction, Instruction):
					instruction.available_registers = set(available_registers)
					if isinstance(instruction, BranchInstruction):
						if i not in processed_branches:
							target_label = instruction.operands[0].label
							target_index = label_table[target_label]
							processed_branches.add(i)
							mark_available_registers(instructions, target_index, available_registers)
						if not instruction.is_conditional():
							return
					else:
						available_registers |= set(instruction.get_output_registers_list())

		current_index = self.find_entry_label()
		mark_available_registers(self.instructions, current_index, set())

	def determine_live_registers(self, exclude_parameter_loads = False):
		self.determine_branches()
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				live_registers = set()
			if isinstance(instruction, BranchInstruction):
				instruction.is_visited = False

		def mark_live_registers(instructions, exit_point, initial_live_registers):
			live_registers = dict(initial_live_registers)
			# Walk from the bottom to top of the linear block
			for i in range(exit_point, -1, -1):
				instruction = instructions[i]
				if isinstance(instruction, BranchInstruction) and not instruction.is_conditional and i != exit_point:
					return
				elif isinstance(instruction, Instruction):
					# First mark registers which are written to by this instruction as non-live
					# Then mark registers which are read by this instruction as live
					for output_register in instruction.get_output_registers_list():
						register_id = output_register.get_id()
						register_mask = output_register.get_mask()
						if register_id in live_registers:
							live_registers[register_id] &= ~register_mask
							if live_registers[register_id] == 0:
								del live_registers[register_id]

					if not (exclude_parameter_loads and isinstance(instruction, LoadParameterPseudoInstruction)):
						for input_register in instruction.get_input_registers_list():
							register_id = input_register.get_id()
							register_mask = input_register.get_mask()
							if register_id in live_registers:
								live_registers[register_id] |= register_mask
							else:
								live_registers[register_id] = register_mask

					# Merge with previously determined as live registers
					for instruction_live_register in instruction.live_registers:
						if instruction_live_register.get_id() in live_registers:
							live_registers[instruction_live_register.get_id()] |= instruction_live_register.get_mask()
						else:
							live_registers[instruction_live_register.get_id()] = instruction_live_register.get_mask()

					instruction.live_registers = set([Register.from_parts(id, mask, expand = True) for (id, mask) in live_registers.iteritems()])
				elif isinstance(instruction, LabelMark):
					for entry_point in instruction.input_branches:
						if not instructions[entry_point].is_visited:
							instructions[entry_point].is_visited = True
							mark_live_registers(instructions, entry_point, live_registers)

		exit_points = self.find_exit_points()
		for exit_point in exit_points:
			mark_live_registers(self.instructions, exit_point, set())

	def check_live_registers(self):
		pass
# 		all_registers = self.abi.volatile_registers + list(reversed(self.abi.argument_registers)) + self.abi.callee_save_registers
# 		available_registers = { Register.GPType: list(), Register.WMMXType: list(), Register.VFPType: list() }
# 		for register in all_registers:
# 			if register not in available_registers[register.type]:
# 				available_registers[register.type].append(register)
# 		for instruction in self.instructions:
# 			live_registers = { Register.GPType: set(), Register.WMMXType: set(), Register.VFPType: set() }
# 			if isinstance(instruction, Instruction):
# 				for live_register in instruction.live_registers:
# 					live_registers[live_register.type].add(live_register)
# 				for register_type in live_registers.iterkeys():
# 					if len(live_registers[register_type]) > len(available_registers[register_type]):
# 						raise ValueError("Not enough available registers to allocate live registers at instruction {0}".format(instruction))

	def determine_register_relations(self):
		all_registers = self.abi.volatile_registers + list(reversed(self.abi.argument_registers)) + self.abi.callee_save_registers
		available_registers = { Register.GPType: list(), Register.WMMXType: list(), Register.VFPType: list() }
		for register in all_registers:
			if register.get_type() == Register.GPType or register.get_type() == Register.WMMXType:
				register_bitboard = 0x1 << register.get_physical_number()
				if register_bitboard not in available_registers[register.type]:
					available_registers[register.get_type()].append(register_bitboard)
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				virtual_live_registers = [register for register in instruction.live_registers if register.is_virtual()]
				for registerX in virtual_live_registers:
					if registerX.get_type() == Register.VFPType:
						if isinstance(registerX, SRegister) and registerX.get_parent():
							registerX = registerX.get_parent()
						if isinstance(registerX, DRegister) and registerX.get_parent():
							registerX = registerX.get_parent()
						if registerX.get_id() not in self.allocation_options:
							if isinstance(registerX, SRegister):
								self.allocation_options[registerX.get_id()] = [(0x1 << n) for n in range(32)]
							elif isinstance(registerX, DRegister):
								if Target.has_vfpd32():
									self.allocation_options[registerX.get_id()] = [(0x3 << n) for n in range(0, 64, 2)]
								else: 
									self.allocation_options[registerX.get_id()] = [(0x3 << n) for n in range(0, 32, 2)]
							else:
								self.allocation_options[registerX.get_id()] = [(0xF << n) for n in range(0, 64, 4)]
					else:
						if registerX.get_id() not in self.allocation_options:
							self.allocation_options[registerX.get_id()] = list(available_registers[registerX.get_type()])

					self.unallocated_registers.append((registerX.get_id(), registerX.get_type()))

					# Setup the list of conflicting registers for each virtual register 
					if registerX.get_id() not in self.conflicting_registers:
						self.conflicting_registers[registerX.get_id()] = set()
					for registerY in virtual_live_registers:
						# VFP registers have a conflict even they are of different size
						if registerX.get_id() != registerY.get_id() and registerX.get_type() == registerY.get_type():
							self.conflicting_registers[registerX.get_id()].add(registerY.get_id())

		# Mark available physical registers for each virtual register
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				virtual_live_registers = [register for register in instruction.live_registers if register.is_virtual()]
				# If a physical register is live at some point, it can not be allocated for a virtual register
				physical_live_registers = [register for register in instruction.live_registers if not register.is_virtual()]
				for virtual_register in virtual_live_registers:
					for physical_register in physical_live_registers:
						if virtual_register.get_type() == physical_register.get_type():
							virtual_register_id = virtual_register.get_id()
							physical_register_bitboard = physical_register.get_bitboard()
							self.allocation_options[virtual_register_id][:] = [possible_register_bitboard for possible_register_bitboard
								in self.allocation_options[virtual_register_id]
								if (possible_register_bitboard & physical_register_bitboard) == 0]

		# Detect group constraints		
		constraints = dict()
		for instruction in self.instructions:
			if isinstance(instruction, NeonLoadStoreInstruction) or isinstance(instruction, VFPLoadStoreMultipleInstruction):
				if isinstance(instruction, NeonLoadStoreInstruction):
					register_list = instruction.operands[0].get_registers_list()
					physical_registers_count = 32
				else:
					register_list = instruction.operands[1].get_registers_list()
					physical_registers_count = 32 if Target.has_vfpd32() else 16
				if len(register_list) > 1:
					if all(isinstance(register, DRegister) for register in register_list):
						register_id_list = list()
						for register in register_list:
							register_id = register.get_id()
							if register_id not in register_id_list:
								register_id_list.append(register_id)
						register_id_list = tuple(register_id_list)
						# Iterate possible allocations for this register list
						# For VLD1/VST1 instructions all registers must be allocated to sequential physical registers
						options = list()
						for sequence_bitboard_position in range(0, 2 * physical_registers_count - 2 * len(register_list) + 2, 2):
							register_bitboards = [0x3 << (sequence_bitboard_position + 2 * i) for i in range(len(register_list))]
							for i, (bitboard, register) in enumerate(zip(register_bitboards, register_list)):
								register_bitboards[i] = register.extend_bitboard(bitboard)
							# Check that bitboard is available for allocation
							for register, bitboard in zip(register_list, register_bitboards):
								if bitboard not in self.allocation_options[register.get_id()]:
									break
							else:
								# Check that if registers with the same id use the same bitboard in this allocation
								register_id_map = dict()
								for register, bitboard in zip(register_list, register_bitboards):
									register_id = register.get_id()
									if register_id in register_id_map:
										if register_id_map[register_id] != bitboard:
											break
									else:
										register_id_map[register_id] = bitboard
								else:
									# Check that allocation bitboards do not overlap:
									allocation_bitboard = 0
									for bitboard in register_id_map.itervalues():
										if (allocation_bitboard & bitboard) == 0:
											allocation_bitboard |= bitboard
										else:
											break
									else:
										ordered_bitboard_list = [register_id_map[register_id] for register_id in register_id_list]
										options.append(tuple(ordered_bitboard_list))
						if options:
							if len(register_id_list) > 1:
								if register_id_list in constraints:
									constraints[register_id_list] = tuple([option for option in constraints[register_id_list] if option in options])
								else:
									constraints[register_id_list] = tuple(options)
						else:
							raise RegisterAllocationError("Imposible virtual register combination in instruction %s" % instruction)
					elif all(isinstance(register, SRegister) for register in register_list) and isinstance(instruction, VFPLoadStoreMultipleInstruction):
						register_id_list = list()
						for register in register_list:
							register_id = register.get_id()
							if register_id not in register_id_list:
								register_id_list.append(register_id)
						register_id_list = tuple(register_id_list)
						# Iterate possible allocations for this register list
						# For VLDM/VSTM instructions all registers must be allocated to sequential physical registers
						options = list()
						for sequence_bitboard_position in range(0, 32 - len(register_list) + 1):
							register_bitboards = [0x1 << (sequence_bitboard_position + i) for i in range(len(register_list))]
							for i, (bitboard, register) in enumerate(zip(register_bitboards, register_list)):
								register_bitboards[i] = register.extend_bitboard(bitboard)
							# Check that bitboard is available for allocation
							for register, bitboard in zip(register_list, register_bitboards):
								if bitboard not in self.allocation_options[register.get_id()]:
									break
							else:
								# Check that if registers with the same id use the same bitboard in this allocation
								register_id_map = dict()
								for register, bitboard in zip(register_list, register_bitboards):
									register_id = register.get_id()
									if register_id in register_id_map:
										if register_id_map[register_id] != bitboard:
											break
									else:
										register_id_map[register_id] = bitboard
								else:
									# Check that allocation bitboards do not overlap:
									allocation_bitboard = 0
									for bitboard in register_id_map.itervalues():
										if (allocation_bitboard & bitboard) == 0:
											allocation_bitboard |= bitboard
										else:
											break
									else:
										ordered_bitboard_list = [register_id_map[register_id] for register_id in register_id_list]
										options.append(tuple(ordered_bitboard_list))
						if options:
							if len(register_id_list) > 1:
								if register_id_list in constraints:
									constraints[register_id_list] = tuple([option for option in constraints[register_id_list] if option in options])
								else:
									constraints[register_id_list] = tuple(options)
						else:
							raise RegisterAllocationError("Imposible virtual register combination in instruction %s" % instruction)
					else:
						assert False
		report_register_constraints = False
		if report_register_constraints:
			for (register_list, options) in constraints.iteritems():
				print "REGISTER CONSTRAINTS: ", map(str, register_list)
				for option in options:
					print "\t", map(lambda t: "%016X" % t, option)

		# Merging of different groups sharing a register will be implemented here sometime

		# Check that each register id appears only once
		constrained_register_id_list = [register_id for register_id_list in constraints.iterkeys() for register_id in register_id_list]
		assert(len(constrained_register_id_list) == len(set(constrained_register_id_list)))
		constrained_register_id_set = set(constrained_register_id_list)
		
		# Create a map from constrained register to constrained register group
# 		constrained_register_map = dict()
# 		for register_id_list in constraints.iterkeys():
# 			for register_id in register_id_list:
# 				constrained_register_map[register_id] = register_id_list 
		
		# Remove individual registers from the set of unallocated registers and add the register group instead
		for constrained_register_id in constrained_register_id_list:
			while (constrained_register_id, Register.VFPType) in self.unallocated_registers: 
				self.unallocated_registers.remove((constrained_register_id, Register.VFPType))
		for register_id_list in constraints.iterkeys():
			self.unallocated_registers.append((register_id_list, Register.VFPType))
		
# 		print "UNALLOCATED REGISTERS:"
# 		print "\t", self.unallocated_registers
		
		# Remove individual registers from the sets of conflicting registers and add the register group instead
# 		for register_id_list in constraints.iterkeys():
# 			self.conflicting_registers[register_id_list] = set()
# 		for constrained_register_id in constrained_register_id_list:
# 			self.conflicting_registers[constrained_register_map[constrained_register_id]].update(self.conflicting_registers[constrained_register_id])
# 			del self.conflicting_registers[constrained_register_id]
# 		for conflicting_registers_set in self.conflicting_registers.itervalues():
# 			for constrained_register_id in constrained_register_id_list:
# 				if constrained_register_id in conflicting_registers_set:
# 					conflicting_registers_set.remove(constrained_register_id)
# 					conflicting_registers_set.add(constrained_register_map[constrained_register_id]) 

		# Remove individual registers from the lists of allocation options and add the register group instead
		for constrained_register_id in constrained_register_id_list:
			del self.allocation_options[constrained_register_id]
		for register_id_list, constrained_options in constraints.iteritems():
			self.allocation_options[register_id_list] = list(options)

	def allocate_registers(self):
		# Map from virtual register id to physical register
		register_allocation = dict()
		for (virtual_register_id, virtual_register_type) in self.unallocated_registers:
			register_allocation[virtual_register_id] = None

		def bind_register(virtual_register_id, physical_register):
			# Remove option to allocate any conflicting virtual register to the same physical register or its enclosing register
			physical_register_bitboard = physical_register.get_bitboard()
			for conflicting_register_id in self.conflicting_registers[virtual_register_id]:
				if conflicting_register_id in self.allocation_options:
					for allocation_bitboard in self.allocation_options[conflicting_register_id]:
						if (allocation_bitboard & physical_register_bitboard) != 0:
							self.allocation_options[conflicting_register_id].remove(allocation_bitboard)
			register_allocation[virtual_register_id] = physical_register

		def bind_registers(virtual_register_id_list, physical_register_id_list):
			# Remove option to allocate any conflicting virtual register to the same physical register or its enclosing register
			physical_register_bitboard_list = [physical_register.get_bitboard() for physical_register in physical_register_id_list]
			for virtual_register_id, physical_register_bitboard in zip(virtual_register_id_list, physical_register_bitboard_list):
				for conflicting_register_id in self.conflicting_registers[virtual_register_id]:
					for allocation_key, allocation_option in self.allocation_options.iteritems():
						if isinstance(allocation_key, tuple):
							if conflicting_register_id in allocation_key:
								conflicting_register_index = allocation_key.index(conflicting_register_id)
								for bitboard_list in allocation_option:
									if (bitboard_list[conflicting_register_index] & physical_register_bitboard) != 0:
										allocation_option.remove(bitboard_list)
						else:
							if conflicting_register_id == allocation_key:
								for bitboard in allocation_option:
									if (bitboard & physical_register_bitboard) != 0:
										allocation_option.remove(bitboard)
				
			for virtual_register_id, physical_register_id in zip(virtual_register_id_list, physical_register_id_list):
				register_allocation[virtual_register_id] = physical_register_id
			

		def is_allocated(virtual_register_id):
			return bool(register_allocation[virtual_register_id])

		# First allocate parameters
		for instruction in self.instructions:
			if isinstance(instruction, LoadParameterPseudoInstruction):
				if instruction.parameter.register:
					if instruction.destination.register.is_virtual():
						if not is_allocated(instruction.destination.register.get_id()):
							if instruction.parameter.register.get_bitboard() in self.allocation_options[instruction.destination.register.get_id()]:
								bind_register(instruction.destination.register.get_id(), instruction.parameter.register)

		# Now allocate registers with special restrictions
		for virtual_register_id_list, virtual_register_type in self.unallocated_registers:
			if isinstance(virtual_register_id_list, tuple):
# 				print "REGLIST: ", map(str, virtual_register_id_list)
				assert self.allocation_options[virtual_register_id_list]
				physical_register_bitboard_list = self.allocation_options[virtual_register_id_list][0]
				physcial_registers_list = [Register.from_bitboard(physical_register_bitboard, virtual_register_type) for physical_register_bitboard in physical_register_bitboard_list]
				bind_registers(virtual_register_id_list, physcial_registers_list)
		
		# Now allocate all other registers
		while self.unallocated_registers:
			virtual_register_id, virtual_register_type = self.unallocated_registers.pop(0)
			if not isinstance(virtual_register_id, tuple):
				if not is_allocated(virtual_register_id):
					assert self.allocation_options[virtual_register_id]
					physical_register_bitboard = self.allocation_options[virtual_register_id][0]
					physical_register = Register.from_bitboard(physical_register_bitboard, virtual_register_type)
					bind_register(virtual_register_id, physical_register)
		
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				for input_register in instruction.get_input_registers_list():
					if input_register.is_virtual():
						input_register.bind(register_allocation[input_register.get_id()])
				for output_register in instruction.get_output_registers_list():
					if output_register.is_virtual():
						if output_register.get_id() in register_allocation:
							output_register.bind(register_allocation[output_register.get_id()])

	# Updates information about registers to be saved/restored in the function prologue/epilogue
	def update_stack_frame(self):
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				self.stack_frame.preserve_registers(instruction.get_output_registers_list())

	def remove_assume_statements(self):
		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, AssumeInitializedPseudoInstruction):
				continue
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions
		
	def generate_parameter_loads(self):
		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, LoadParameterPseudoInstruction):
				parameter = instruction.parameter
				if parameter.register:
					# If parameter is in a register, use register-register move:
					if instruction.destination.register != parameter.register:
						# Parameter is in a different register than instruction destination, generate move:
						new_instruction = MOV( instruction.destination.register, parameter.register )
						new_instruction.live_registers = instruction.live_registers
						new_instruction.available_registers = instruction.available_registers
						new_instructions.append(new_instruction)
					# If parameter is in the same register as instruction destination, no instruction needed:
					#   MOV( instruction.destination == parameter.register_location, parameter.register_location )
					# is a no-op
				else:
					parameter_address = self.stack_frame.get_parameters_offset() + parameter.stack_offset
					new_instruction = LDR( instruction.destination.register, [sp, parameter_address] )
					new_instruction.live_registers = instruction.live_registers
					new_instruction.available_registers = instruction.available_registers
					new_instructions.append(new_instruction)
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions

	def generate_constant_loads(self):
		max_alignment = 0
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				constant = instruction.get_constant()
				if constant is not None:
					constant_alignment = constant.get_alignment()
					constant_size = constant.size * constant.repeats
					max_alignment = max(max_alignment, constant_alignment)

		constant_id = 0
		constant_label_map = dict()
		constant_buckets = dict()
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				constant = instruction.get_constant()
				if constant is not None:
					if constant in constant_label_map:
						constant.label = constant_label_map[constant]
					else:
						constant.label = "c" + str(constant_id)
						constant_id += 1
						constant_label_map[constant] = constant.label
						constant_alignment = constant.get_alignment()
						constant_size = constant.size * constant.repeats
						if constant_alignment in constant_buckets:
							constant_buckets[constant_alignment].add(constant)
							if constant_buckets[constant_alignment].is_full():
								del constant_buckets[constant_alignment]
						else:
							constant_bucket = ConstantBucket(max_alignment / 8)
							constant_bucket.add(constant)
							self.constants.append(constant_bucket)
							if not constant_bucket.is_full():
								constant_buckets[constant_alignment] = constant_bucket

		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, LoadConstantPseudoInstruction):
				constant = instruction.source.constant
				if constant.basic_type == 'float32':
					if constant.size * constant.repeats == 128:
						if self.uses_avx:
							new_instruction = VMOVAPS( instruction.destination.register, instruction.source.constant )
						else:
							new_instruction = MOVAPS( instruction.destination.register, instruction.source.constant )
					elif constant.size * constant.repeats == 256:
						assert self.uses_avx
						new_instruction = VMOVAPS( instruction.destination.register, instruction.source.constant )
					elif constant.size == 32 and constant.repeats == 1:
						if self.uses_avx:
							new_instruction = VMOVSS( instruction.destination.register, instruction.source.constant )
						else:
							new_instruction = MOVSS( instruction.destination.register, instruction.source.constant )
				elif constant.basic_type == 'float64':
					if constant.size * constant.repeats == 128:
						if self.uses_avx:
							new_instruction = VMOVAPD( instruction.destination.register, instruction.source.constant )
						else:
							new_instruction = MOVAPD( instruction.destination.register, instruction.source.constant )
					elif constant.size * constant.repeats == 256:
						assert self.uses_avx
						new_instruction = VMOVAPS( instruction.destination.register, instruction.source.constant )
					elif constant.size == 64 and constant.repeats == 1:
						if self.uses_avx:
							new_instruction = VMOVSD( instruction.destination.register, instruction.source.constant )
						else:
							new_instruction = MOVSD( instruction.destination.register, instruction.source.constant )
				else:
					if self.uses_avx:
						new_instruction = VMOVDQA( instruction.destination.register, instruction.source.constant )
					else:
						new_instruction = MOVDQA( instruction.destination.register, instruction.source.constant )
				new_instructions.append(new_instruction)
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions

	def optimize_instructions(self):
 		new_instructions = list()
 		for instruction in self.instructions:
 			# Remove moves where source and destination are the same
 			
 			if isinstance(instruction, MovInstruction):
 				if len(instruction.operands) != 2 or instruction.operands[0] != instruction.operands[1]:
 					new_instructions.append(instruction)
 			elif isinstance(instruction, VfpNeonMovInstruction):
 				if instruction.operands[0] != instruction.operands[1]:
 					new_instructions.append(instruction)
 			else:
 				new_instructions.append(instruction)
 		self.instructions = new_instructions

	def get_target(self):
		return self.target

	def get_isa_extensions(self):
		isa_extensions = set()
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				isa_extensions.add(instruction.get_isa_extension())
				registers_list = instruction.get_registers_list()
				if any(isinstance(register, QRegister) or isinstance(register, DRegister) and register.is_extended() for register in instruction.get_registers_list()):
					isa_extensions.add("VFPd32")
		if 'NEON' in isa_extensions or 'NEONHP' in isa_extensions or 'NEON2' in isa_extensions:
			if 'VFPd32' in isa_extensions:
				isa_extensions.remove('VFPd32')
		return list(isa_extensions)

	def get_yeppp_isa_extensions(self):
		isa_extensions_map = {'V4':              ('V4',        None,      None),
		                      'V5':              ( 'V5',       None,      None),
		                      'V5E':             ( 'V5E',      None,      None),
		                      'V6':              ( 'V6',       None,      None),
		                      'V6K':             ( 'V6K',      None,      None),
		                      'V7':              ( 'V7',       None,      None),
		                      'V7MP':            ( 'V7MP',     None,      None),
		                      'Div':             ( 'Div',      None,      None),
		                      'Thumb':           ( 'Thumb',    None,      None),
		                      'Thumb2':          ( 'Thumb2',   None,      None),
		                      'VFP':             ( 'VFP',      None,      None),
		                      'VFP2':            ( 'VFP2',     None,      None),
		                      'VFP3':            ( 'VFP3',     None,      None),
		                      'VFPd32':          ( 'VFPd32',   None,      None),
		                      'VFP3HP':          ( 'VFP3HP',   None,      None),
		                      'VFP4':            ( 'VFP4',     None,      None),
		                      'VFPVectorMode':   ( None,       None,      'VFPVectorMode'),
		                      'XScale':          ( None,       'XScale',  None),
		                      'WMMX':            ( None,       'WMMX',    None),
		                      'WMMX2':           ( None,       'WMMX2',   None),
		                      'NEON':            ( None,       'NEON',    None),
		                      'NEONHP':          ( None,       'NEONHP',  None),
		                      'NEON2':           ( None,       'NEON2',   None)}
		(isa_extensions, simd_extensions, system_extensions) = (set(), set(), set())
		for isa_extension in self.get_isa_extensions():
			if isa_extension is not None:
				(isa_extension, simd_extension, system_extension) = isa_extensions_map[isa_extension]
				if isa_extension is not None:
					isa_extensions.add(isa_extension)
				if simd_extension is not None:
					simd_extensions.add(simd_extension)
				if system_extension is not None:
					system_extensions.add(system_extension)
		isa_extensions = map(lambda id: "YepARMIsaFeature" + id, isa_extensions)
		if not isa_extensions:
			isa_extensions = ["YepIsaFeaturesDefault"]
		simd_extensions = map(lambda id: "YepARMSimdFeature" + id, simd_extensions)
		if not simd_extensions:
			simd_extensions = ["YepSimdFeaturesDefault"]
		system_extensions = map(lambda id: "YepARMSystemFeature" + id, system_extensions)
		if not system_extensions:
			system_extensions = ["YepSystemFeaturesDefault"]
		return (isa_extensions, simd_extensions, system_extensions)

	def allocate_local_variable(self):
		self.local_variables_count += 1
		return self.local_variables_count

	def allocate_q_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x0F0

	def allocate_d_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x300

	def allocate_s_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x400

	def allocate_wmmx_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x002

	def allocate_general_purpose_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x001

class LocalVariable(object):
	def __init__(self, register_type):
		super(LocalVariable, self).__init__()
		if isinstance(register_type, int):
			self.size = register_type
		elif register_type == GeneralPurposeRegister:
			self.size = 4
		elif register_type == WMMXRegister:
			self.size = 8
		elif register_type == SRegister:
			self.size = 4
		elif register_type == DRegister:
			self.size = 8
		elif register_type == QRegister:
			self.size = 16
		else:
			raise ValueError('Unsupported register type {0}'.format(register_type))
		self.id = current_function.allocate_local_variable()
		self.address = None
		self.offset = 0
		self.parent = None

	def __eq__(self, other):
		return self.id == other.id

	def __hash__(self):
		return hash(self.id)

	def __str__(self):
		if self.is_subvariable():
			address = self.parent.get_address()
			if address is not None:
				address += self.offset
		else:
			address = self.address
		if address is not None:
			return "[{0}]".format(address)
		else:
			return "local-variable<{0}>".format(self.id)

	def is_subvariable(self):
		return self.parent is not None

	def get_parent(self):
		return self.parent
	
	def get_root(self):
		if self.is_subvariable():
			return self.get_parent().get_root()
		else:
			return self

	def get_address(self):
		if self.is_subvariable():
			return self.parent.get_address() + self.offset
		else:
			return self.address

	def get_size(self):
		return self.size

	def get_low(self):
		assert self.get_size() % 2 == 0
		child = LocalVariable(self.get_size() / 2)
		child.parent = self
		child.offset = 0
		return child

	def get_high(self):
		assert self.get_size() % 2 == 0
		child = LocalVariable(self.get_size() / 2)
		child.parent = self
		child.offset = self.get_size() / 2
		return child

class StackFrame(object):
	def __init__(self, abi):
		super(StackFrame, self).__init__()
		self.abi = abi
		self.general_purpose_registers = list()
		self.d_registers = list()
		self.s_variables = list()
		self.d_variables = list()
		self.q_variables = list()

	def preserve_registers(self, registers):
		for register in registers:
			self.preserve_register(register)

	def preserve_register(self, register):
		if isinstance(register, GeneralPurposeRegister):
			if not register in self.general_purpose_registers:
				if register in self.abi.callee_save_registers:
					self.general_purpose_registers.append(register)
		elif isinstance(register, SRegister):
			if not register.is_virtual():
				register = register.get_parent()
				if not register in self.d_registers:
					if register in self.abi.callee_save_registers:
						self.d_registers.append(register)
		elif isinstance(register, DRegister):
			if not register in self.d_registers:
				if register in self.abi.callee_save_registers:
					self.d_registers.append(register)
		elif isinstance(register, QRegister):
			d_low  = register.get_low_part()
			d_high = register.get_high_part()
			if d_low not in self.d_registers:
				if register in self.abi.callee_save_registers:
					self.d_registers.append(d_low)
			if d_high not in self.d_registers:
				if register in self.abi.callee_save_registers:
					self.d_registers.append(d_high)
		else:
			raise TypeError("Unsupported register type {0}".format(type(register)))

	def add_variable(self, variable):
		if variable.get_size() == 16:
			if variable not in self.sse_variables:
				self.sse_variables.append(variable)
		elif variable.get_size() == 32:
			if variable not in self.avx_variables:
				self.avx_variables.append(variable)
		else:
			raise TypeError("Unsupported variable type {0}".format(type(variable)))

	def get_parameters_offset(self):
		parameters_offset = len(self.general_purpose_registers) * 4
		if parameters_offset % 8 == 4:
			parameters_offset += 4
		return parameters_offset + len(self.d_registers) * 8 

	def generate_prologue(self):
		with InstructionStream() as instructions:
			if self.general_purpose_registers:
				general_purpose_registers = list(self.general_purpose_registers)
				if len(general_purpose_registers) % 2 == 1:
					general_purpose_registers.append(r3)
				PUSH( tuple(sorted(general_purpose_registers, key = lambda reg: reg.get_physical_number() )) )
			if self.d_registers:
				VPUSH( tuple(sorted(self.d_registers, key = lambda reg: reg.get_physical_number() )) ) 
		return list(iter(instructions))

	def generate_epilogue(self):
		with InstructionStream() as instructions:
			if self.d_registers:
				VPOP( tuple(sorted(self.d_registers, key = lambda reg: reg.get_physical_number() )) ) 
			if self.general_purpose_registers:
				general_purpose_registers = list(self.general_purpose_registers)
				if len(general_purpose_registers) % 2 == 1:
					general_purpose_registers.append(r3)
				POP( tuple(sorted(general_purpose_registers, key = lambda reg: reg.get_physical_number() )) )
		return list(iter(instructions))

class Register(object):
	GPType   = 1
	WMMXType = 2
	VFPType  = 3
	
	def __init__(self):
		super(Register, self).__init__()

	def __lt__(self, other):
		return self.number < other.number

	def __le__(self, other):
		return self.number <= other.number

	def __eq__(self, other):
		return isinstance(other, Register) and self.number == other.number

	def __ne__(self, other):
		return not isinstance(other, Register) or self.number != other.number

	def __gt__(self, other):
		return self.number > other.number

	def __ge__(self, other):
		return self.number >= other.number

	def __contains__(self, register):
		if self.get_id() == register.get_id():
			register_mask = register.get_mask()
			return ((self.get_mask() & register_mask) == register_mask)
		else:
			return False

	def __hash__(self):
		return self.number

	def get_id(self):
		return self.number >> 12

	def get_mask(self):
		return (self.number & 0xFFF)

	def get_type(self):
		return self.type

	def get_size(self):
		return self.size

	def get_bitboard(self):
		assert not self.is_virtual()
		if isinstance(self, GeneralPurposeRegister) or isinstance(self, WMMXRegister) or isinstance(self, SRegister):
			return 0x1 << self.get_physical_number()
		elif isinstance(self, DRegister):
			return 0x3 << (self.get_physical_number() * 2)
		elif isinstance(self, QRegister):
			return 0xF << (self.get_physical_number() * 4)

	@staticmethod
	def from_parts(id, mask, expand = False):
		if mask == 0x001:
			# General-purpose register
			return GeneralPurposeRegister((id << 12) | mask)
		elif mask == 0x002:
			# WMMX register
			return WMMXRegister((id << 12) | 0x002)
		elif (mask & ~0x7F0) == 0x000:
			# VFP or NEON register
			if ((mask & 0x7F0) == 0x0F0):
				return QRegister((id << 12) | mask)
			elif ((mask & 0x7F0) == 0x030) or ((mask & 0x7F0) == 0x0C0) or ((mask & 0x7F0) == 0x300):
				return DRegister((id << 12) | mask)
			elif (mask & (mask - 1)) == 0:
				return SRegister((id << 12) | mask)
			else:
				if expand and ((mask & ~0x0F0) == 0):
					return QRegister((id << 12) | 0x0F0)
				else:
					raise ValueError("Invalid register mask %s" % hex(mask))
		else:
			raise ValueError("Invalid register mask %s" % hex(mask))

	@staticmethod
	def from_bitboard(bitboard, type):
		if type == Register.GPType:
			return {0x0001: r0,
			        0x0002: r1,
			        0x0004: r2,
			        0x0008: r3,
			        0x0010: r4,
			        0x0020: r5,
			        0x0040: r6,
			        0x0080: r7,
			        0x0100: r8,
			        0x0200: r9,
			        0x0400: r10,
			        0x0800: r11,
			        0x1000: r12,
			        0x2000: sp,
			        0x4000: lr,
			        0x8000: pc}[bitboard]
		elif type == Register.WMMXType:
			return {0x0001: wr0,
			        0x0002: wr1,
			        0x0004: wr2,
			        0x0008: wr3,
			        0x0010: wr4,
			        0x0020: wr5,
			        0x0040: wr6,
			        0x0080: wr7,
			        0x0100: wr8,
			        0x0200: wr9,
			        0x0400: wr10,
			        0x0800: wr11,
			        0x1000: wr12,
			        0x2000: wr13,
			        0x4000: wr14,
			        0x8000: wr15}[bitboard]
		elif type == Register.VFPType:
			return {0x00000001: s0,
			        0x00000002: s1,
			        0x00000004: s2,
			        0x00000008: s3,
			        0x00000010: s4,
			        0x00000020: s5,
			        0x00000040: s6,
			        0x00000080: s7,
			        0x00000100: s8,
			        0x00000200: s9,
			        0x00000400: s10,
			        0x00000800: s11,
			        0x00001000: s12,
			        0x00002000: s13,
			        0x00004000: s14,
			        0x00008000: s15,
			        0x00010000: s16,
			        0x00020000: s17,
			        0x00040000: s18,
			        0x00080000: s19,
			        0x00100000: s20,
			        0x00200000: s21,
			        0x00400000: s22,
			        0x00800000: s23,
			        0x01000000: s24,
			        0x02000000: s25,
			        0x04000000: s26,
			        0x08000000: s27,
			        0x10000000: s28,
			        0x20000000: s29,
			        0x40000000: s30,
			        0x80000000: s31,
			        0x0000000000000003: d0,
			        0x000000000000000C: d1,
			        0x0000000000000030: d2,
			        0x00000000000000C0: d3,
			        0x0000000000000300: d4,
			        0x0000000000000C00: d5,
			        0x0000000000003000: d6,
			        0x000000000000C000: d7,
			        0x0000000000030000: d8,
			        0x00000000000C0000: d9,
			        0x0000000000300000: d10,
			        0x0000000000C00000: d11,
			        0x0000000003000000: d12,
			        0x000000000C000000: d13,
			        0x0000000030000000: d14,
			        0x00000000C0000000: d15,
			        0x0000000300000000: d16,
			        0x0000000C00000000: d17,
			        0x0000003000000000: d18,
			        0x000000C000000000: d19,
			        0x0000030000000000: d20,
			        0x00000C0000000000: d21,
			        0x0000300000000000: d22,
			        0x0000C00000000000: d23,
			        0x0003000000000000: d24,
			        0x000C000000000000: d25,
			        0x0030000000000000: d26,
			        0x00C0000000000000: d27,
			        0x0300000000000000: d28,
			        0x0C00000000000000: d29,
			        0x3000000000000000: d30,
			        0xC000000000000000: d31,
			        0x000000000000000F: q0,
			        0x00000000000000F0: q1,
			        0x0000000000000F00: q2,
			        0x000000000000F000: q3,
			        0x00000000000F0000: q4,
			        0x0000000000F00000: q5,
			        0x000000000F000000: q6,
			        0x00000000F0000000: q7,
			        0x0000000F00000000: q8,
			        0x000000F000000000: q9,
			        0x00000F0000000000: q10,
			        0x0000F00000000000: q11,
			        0x000F000000000000: q12,
			        0x00F0000000000000: q13,
			        0x0F00000000000000: q14,
			        0xF000000000000000: q15}[bitboard]

	def extend_bitboard(self, bitboard):
		physical_register = Register.from_bitboard(bitboard, self.type)
		if isinstance(self, SRegister) and self.get_parent() and self.get_parent().get_parent():
			physical_register = physical_register.get_parent().get_parent()
		elif (isinstance(self, SRegister) or isinstance(self, DRegister)) and self.get_parent():
			physical_register = physical_register.get_parent()
		return physical_register.get_bitboard()

	def is_virtual(self):
		return self.number >= 0x40000

	def bind(self, register):
		assert self.is_virtual()
		assert not register.is_virtual()
		if isinstance(register, GeneralPurposeRegister) or isinstance(register, WMMXRegister):
			self.number = (self.number & 0xFFF) | (register.get_id() << 12)
		elif isinstance(register, SRegister):
			self.number = register.number
		elif isinstance(register, DRegister):
			if isinstance(self, DRegister):
				self.number = register.number
			elif isinstance(self, SRegister):
				if register.get_mask() == 0x030 and self.get_mask() == 0x100:
					self.number = (register.get_id() << 12) | 0x010
				elif register.get_mask() == 0x030 and self.get_mask() == 0x200:
					self.number = (register.get_id() << 12) | 0x020
				elif register.get_mask() == 0x0C0 and self.get_mask() == 0x100:
					self.number = (register.get_id() << 12) | 0x040
				elif register.get_mask() == 0x0C0 and self.get_mask() == 0x200:
					self.number = (register.get_id() << 12) | 0x080
				else:
					assert False
			else:
				assert False
		elif isinstance(register, QRegister):
			if isinstance(self, QRegister):
				self.number = register.number
			elif isinstance(self, DRegister):
				self.number = (register.get_id() << 12) | (self.get_mask())
			elif isinstance(self, SRegister):
				self.number = (register.get_id() << 12) | (self.get_mask())
			else:
				assert False
		assert not self.is_virtual()

class GeneralPurposeRegister(Register):
	name_to_number_map = {'r0' : 0x20001,
	                      'a1' : 0x20001,
	                      'r1' : 0x21001,
	                      'a2' : 0x21001,
	                      'r2' : 0x22001,
	                      'a3' : 0x22001,
	                      'r3' : 0x23001,
	                      'a4' : 0x23001,
	                      'r4' : 0x24001,
	                      'r5' : 0x25001,
	                      'r6' : 0x26001,
	                      'r7' : 0x27001,
	                      'r8' : 0x28001,
	                      'r9' : 0x29001,
	                      'sb' : 0x29001,
	                      'r10': 0x2A001,
	                      'r11': 0x2B001,
	                      'r12': 0x2C001,
	                      'ip' : 0x2C001,
	                      'r13': 0x2D001,
	                      'sp' : 0x2D001,
	                      'r14': 0x2E001,
	                      'lr' : 0x2E001,
	                      'r15': 0x2F001,
	                      'pc' : 0x2F001}

	number_to_name_map = {0x20001: 'r0',
	                      0x21001: 'r1',
	                      0x22001: 'r2',
	                      0x23001: 'r3',
	                      0x24001: 'r4',
	                      0x25001: 'r5',
	                      0x26001: 'r6',
	                      0x27001: 'r7',
	                      0x28001: 'r8',
	                      0x29001: 'r9',
	                      0x2A001: 'r10',
	                      0x2B001: 'r11',
	                      0x2C001: 'r12',
	                      0x2D001: 'sp',
	                      0x2E001: 'lr',
	                      0x2F001: 'pc'}

	def __init__(self, id = None):
		super(GeneralPurposeRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_general_purpose_register()
			self.type = Register.GPType
			self.size = 4
		elif isinstance(id, int):
			self.number = id
			self.type = Register.GPType
			self.size = 4
		elif isinstance(id, str):
			if id in GeneralPurposeRegister.name_to_number_map.iterkeys():
				self.number = GeneralPurposeRegister.name_to_number_map[id]
				self.type = Register.GPType
				self.size = 4
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, GeneralPurposeRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id  is neither a name of an architectural general-purpose register, nor an id of a virtual register')

	def get_physical_number(self):
		return {0x20001: 0,
		        0x21001: 1,
		        0x22001: 2,
		        0x23001: 3,
		        0x24001: 4,
		        0x25001: 5,
		        0x26001: 6,
		        0x27001: 7,
		        0x28001: 8,
		        0x29001: 9,
		        0x2A001: 10,
		        0x2B001: 11,
		        0x2C001: 12,
		        0x2D001: 13,
		        0x2E001: 14,
		        0x2F001: 15}[self.number]

	def is_compatible_bitboard(self, bitboard):
		return bitboard in {0x0001, 0x0002, 0x0004, 0x0008,
		                    0x0010, 0x0020, 0x0040, 0x0080,
		                    0x0100, 0x0200, 0x0400, 0x0800,
		                    0x1000, 0x2000, 0x4000, 0x8000}

	def __str__(self):
		if self.is_virtual():
			return 'gp-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return GeneralPurposeRegister.number_to_name_map[self.number]

	def __neg__(self):
		return NegatedGeneralPurposeRegister(self)

	def wb(self):
		return GeneralPurposeRegisterWriteback(self)

	def LSL(self, shift):
		return ShiftedGeneralPurposeRegister(self, "LSL", shift)

	def LSR(self, shift):
		return ShiftedGeneralPurposeRegister(self, "LSR", shift)

	def ASR(self, shift):
		return ShiftedGeneralPurposeRegister(self, "ASR", shift)

	def ROR(self, shift):
		return ShiftedGeneralPurposeRegister(self, "ROR", shift)

	def RRX(self):
		return ShiftedGeneralPurposeRegister(self, "RRX")

r0  = GeneralPurposeRegister('r0')
r1  = GeneralPurposeRegister('r1')
r2  = GeneralPurposeRegister('r2')
r3  = GeneralPurposeRegister('r3')
r4  = GeneralPurposeRegister('r4')
r5  = GeneralPurposeRegister('r5')
r6  = GeneralPurposeRegister('r6')
r7  = GeneralPurposeRegister('r7')
r8  = GeneralPurposeRegister('r8')
r9  = GeneralPurposeRegister('r9')
r10 = GeneralPurposeRegister('r10')
r11 = GeneralPurposeRegister('r11')
r12 = GeneralPurposeRegister('r12')
sp  = GeneralPurposeRegister('sp')
lr  = GeneralPurposeRegister('lr')
pc  = GeneralPurposeRegister('pc')

class GeneralPurposeRegisterWriteback(GeneralPurposeRegister):
	def __init__(self, register):
		if isinstance(register, GeneralPurposeRegister):
			super(GeneralPurposeRegisterWriteback, self).__init__(register)
			self.register = register
		else:
			raise TypeError('Register parameter is not an instance of GeneralPurposeRegister')

	def __str__(self):
		return str(self.register) + "!"

class NegatedGeneralPurposeRegister:
	def __init__(self, register):
		if isinstance(register, GeneralPurposeRegister):
			self.register = register
		else:
			raise TypeError('Register parameter is not an instance of GeneralPurposeRegister')

	def __str__(self):
		return "-" + str(self.register)

class ShiftedGeneralPurposeRegister:
	def __init__(self, register, type, shift = None):
		if isinstance(register, GeneralPurposeRegister):
			self.register = register
			if type in {'LSR', 'ASR'}:
				if 1 <= shift <= 32:
					self.shift = int(shift)
					self.type = type
				else:
					raise ValueError("Shift is beyond the allowed range (1 to 32)")
			elif type in {'LSL', 'ROR'}:
				if 1 <= shift <= 31:
					self.shift = int(shift)
					self.type = type
				else:
					raise ValueError("Shift is beyond the allowed range (1 to 31)")
			elif type == 'RRX':
				if shift is None:
					self.shift = shift
					self.type = type
				else:
					raise ValueError("Shift parameter is not allowed for RRX modificator")
			else:
				raise ValueError("Illegal shift type %s" % type)
		else:
			raise TypeError("Register parameter must be a general-purpose register")

	def __str__(self):
		if self.type != 'RRX':
			return str(self.register) + ", " + self.type + " #" + str(self.shift)
		else:
			return str(self.register) + ", " + self.type

class WMMXRegister(Register):
	name_to_number_map = {'wr0' : 0x10002,
	                      'wr1' : 0x11002,
	                      'wr2' : 0x12002,
	                      'wr3' : 0x13002,
	                      'wr4' : 0x14002,
	                      'wr5' : 0x15002,
	                      'wr6' : 0x16002,
	                      'wr7' : 0x17002,
	                      'wr8' : 0x18002,
	                      'wr9' : 0x19002,
	                      'wr10': 0x1A002,
	                      'wr11': 0x1B002,
	                      'wr12': 0x1C002,
	                      'wr13': 0x1D002,
	                      'wr14': 0x1E002,
	                      'wr15': 0x1F002}

	number_to_name_map = {0x10002: 'wr0',
	                      0x11002: 'wr1',
	                      0x12002: 'wr2',
	                      0x13002: 'wr3',
	                      0x14002: 'wr4',
	                      0x15002: 'wr5',
	                      0x16002: 'wr6',
	                      0x17002: 'wr7',
	                      0x18002: 'wr8',
	                      0x19002: 'wr9',
	                      0x1A002: 'wr10',
	                      0x1B002: 'wr11',
	                      0x1C002: 'wr12',
	                      0x1D002: 'wr13',
	                      0x1E002: 'wr14',
	                      0x1F002: 'wr15'}

	def __init__(self, id = None):
		super(WMMXRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_wmmx_register()
			self.type = Register.WMMXType
			self.size = 8
		elif isinstance(id, int):
			self.number = id
			self.type = Register.WMMXType
			self.size = 8
		elif isinstance(id, str):
			if id in WMMXRegister.name_to_number_map.iterkeys():
				self.number = WMMXRegister.name_to_number_map[id]
				self.type = Register.WMMXType
				self.size = 8
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, WMMXRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural mmx register, nor an id of a virtual register')

	def is_compatible_bitboard(self, bitboard):
		return bitboard in {0x0001, 0x0002, 0x0004, 0x0008,
		                    0x0010, 0x0020, 0x0040, 0x0080,
		                    0x0100, 0x0200, 0x0400, 0x0800,
		                    0x1000, 0x2000, 0x4000, 0x8000}

	def __str__(self):
		if self.is_virtual():
			return 'wmmx-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return WMMXRegister.number_to_name_map[self.number]

wr0  = WMMXRegister('wr0')
wr1  = WMMXRegister('wr1')
wr2  = WMMXRegister('wr2')
wr3  = WMMXRegister('wr3')
wr4  = WMMXRegister('wr4')
wr5  = WMMXRegister('wr5')
wr6  = WMMXRegister('wr6')
wr7  = WMMXRegister('wr7')
wr8  = WMMXRegister('wr8')
wr9  = WMMXRegister('wr9')
wr10 = WMMXRegister('wr10')
wr11 = WMMXRegister('wr11')
wr12 = WMMXRegister('wr12')
wr13 = WMMXRegister('wr13')
wr14 = WMMXRegister('wr14')
wr15 = WMMXRegister('wr15')

class SRegister(Register):
	name_to_number_map = {'s0' : 0x00010,
	                      's1' : 0x00020,
	                      's2' : 0x00040,
	                      's3' : 0x00080,
	                      's4' : 0x01010,
	                      's5' : 0x01020,
	                      's6' : 0x01040,
	                      's7' : 0x01080,
	                      's8' : 0x02010,
	                      's9' : 0x02020,
	                      's10': 0x02040,
	                      's11': 0x02080,
	                      's12': 0x03010,
	                      's13': 0x03020,
	                      's14': 0x03040,
	                      's15': 0x03080,
	                      's16': 0x04010,
	                      's17': 0x04020,
	                      's18': 0x04040,
	                      's19': 0x04080,
	                      's20': 0x05010,
	                      's21': 0x05020,
	                      's22': 0x05040,
	                      's23': 0x05080,
	                      's24': 0x06010,
	                      's25': 0x06020,
	                      's26': 0x06040,
	                      's27': 0x06080,
	                      's28': 0x07010,
	                      's29': 0x07020,
	                      's30': 0x07040,
	                      's31': 0x07080}

	number_to_name_map = {0x00010: 's0',
	                      0x00020: 's1',
	                      0x00040: 's2',
	                      0x00080: 's3',
	                      0x01010: 's4',
	                      0x01020: 's5',
	                      0x01040: 's6',
	                      0x01080: 's7',
	                      0x02010: 's8',
	                      0x02020: 's9',
	                      0x02040: 's10',
	                      0x02080: 's11',
	                      0x03010: 's12',
	                      0x03020: 's13',
	                      0x03040: 's14',
	                      0x03080: 's15',
	                      0x04010: 's16',
	                      0x04020: 's17',
	                      0x04040: 's18',
	                      0x04080: 's19',
	                      0x05010: 's20',
	                      0x05020: 's21',
	                      0x05040: 's22',
	                      0x05080: 's23',
	                      0x06010: 's24',
	                      0x06020: 's25',
	                      0x06040: 's26',
	                      0x06080: 's27',
	                      0x07010: 's28',
	                      0x07020: 's29',
	                      0x07040: 's30',
	                      0x07080: 's31'}

	def __init__(self, id = None):
		super(SRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_s_register()
			self.type = Register.VFPType
			self.size = 4
		elif isinstance(id, int):
			self.number = id
			self.type = Register.VFPType
			self.size = 4
		elif isinstance(id, str):
			if id in SRegister.name_to_number_map.iterkeys():
				self.number = SRegister.name_to_number_map[id]
				self.type = Register.VFPType
				self.size = 4
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, SRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural S register, nor an id of a virtual register')

	def get_physical_number(self):
		assert not self.is_virtual()
		return {0x00010: 0,
		        0x00020: 1,
		        0x00040: 2,
		        0x00080: 3,
		        0x01010: 4,
		        0x01020: 5,
		        0x01040: 6,
		        0x01080: 7,
		        0x02010: 8,
		        0x02020: 9,
		        0x02040: 10,
		        0x02080: 11,
		        0x03010: 12,
		        0x03020: 13,
		        0x03040: 14,
		        0x03080: 15,
		        0x04010: 16,
		        0x04020: 17,
		        0x04040: 18,
		        0x04080: 19,
		        0x05010: 20,
		        0x05020: 21,
		        0x05040: 22,
		        0x05080: 23,
		        0x06010: 24,
		        0x06020: 25,
		        0x06040: 26,
		        0x06080: 27,
		        0x07010: 28,
		        0x07020: 29,
		        0x07040: 30,
		        0x07080: 31}[self.number]

	def is_compatible_bitboard(self, bitboard):
		if self.get_mask() == 0x400:
			return bitboard in {0x00000001, 0x00000002, 0x00000004, 0x00000008,
			                    0x00000010, 0x00000020, 0x00000040, 0x00000080,
			                    0x00000100, 0x00000200, 0x00000400, 0x00000800,
			                    0x00001000, 0x00002000, 0x00004000, 0x00008000,
			                    0x00010000, 0x00020000, 0x00040000, 0x00080000,
			                    0x00100000, 0x00200000, 0x00400000, 0x00800000,
			                    0x01000000, 0x02000000, 0x04000000, 0x08000000,
			                    0x10000000, 0x20000000, 0x40000000, 0x80000000}
		elif self.get_mask() == 0x200:
			return bitboard in {0x00000002, 0x00000008,
			                    0x00000020, 0x00000080,
			                    0x00000200, 0x00000800,
			                    0x00002000, 0x00008000,
			                    0x00020000, 0x00080000,
			                    0x00200000, 0x00800000,
			                    0x02000000, 0x08000000,
			                    0x20000000, 0x80000000}
		elif self.get_mask() == 0x100:
			return bitboard in {0x00000001, 0x00000004,
			                    0x00000010, 0x00000040,
			                    0x00000100, 0x00000400,
			                    0x00001000, 0x00004000,
			                    0x00010000, 0x00040000,
			                    0x00100000, 0x00400000,
			                    0x01000000, 0x04000000,
			                    0x10000000, 0x40000000}
		elif self.get_mask() == 0x080:
			return bitboard in {0x00000008, 0x00000080, 0x00000800, 0x00008000, 0x00080000, 0x00800000, 0x08000000, 0x80000000}
		elif self.get_mask() == 0x040:
			return bitboard in {0x00000004, 0x00000040, 0x00000400, 0x00004000, 0x00040000, 0x00400000, 0x04000000, 0x40000000}
		elif self.get_mask() == 0x020:
			return bitboard in {0x00000002, 0x00000020, 0x00000200, 0x00002000, 0x00020000, 0x00200000, 0x02000000, 0x20000000}
		elif self.get_mask() == 0x010:
			return bitboard in {0x00000001, 0x00000010, 0x00000100, 0x00001000, 0x00010000, 0x00100000, 0x01000000, 0x10000000}
		else:
			assert False

	def __str__(self):
		if self.is_virtual():
			return 's-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return SRegister.number_to_name_map[self.number]

	def get_parent(self):
		mask = self.get_mask()
		parent_mask = {0x400: None,  0x200: 0x300, 0x100: 0x300,
		               0x080: 0x0C0, 0x040: 0x0C0, 0x020: 0x030, 0x010: 0x030}[mask]
		if parent_mask:
			return DRegister(self.number | parent_mask)

s0  = SRegister('s0')
s1  = SRegister('s1')
s2  = SRegister('s2')
s3  = SRegister('s3')
s4  = SRegister('s4')
s5  = SRegister('s5')
s6  = SRegister('s6')
s7  = SRegister('s7')
s8  = SRegister('s8')
s9  = SRegister('s9')
s10 = SRegister('s10')
s11 = SRegister('s11')
s12 = SRegister('s12')
s13 = SRegister('s13')
s14 = SRegister('s14')
s15 = SRegister('s15')
s16 = SRegister('s16')
s17 = SRegister('s17')
s18 = SRegister('s18')
s19 = SRegister('s19')
s20 = SRegister('s20')
s21 = SRegister('s21')
s22 = SRegister('s22')
s23 = SRegister('s23')
s24 = SRegister('s24')
s25 = SRegister('s25')
s26 = SRegister('s26')
s27 = SRegister('s27')
s28 = SRegister('s28')
s29 = SRegister('s29')
s30 = SRegister('s30')
s31 = SRegister('s31')

class DRegister(Register):
	name_to_number_map = {'d0' : 0x00030,
	                      'd1' : 0x000C0,
	                      'd2' : 0x01030,
	                      'd3' : 0x010C0,
	                      'd4' : 0x02030,
	                      'd5' : 0x020C0,
	                      'd6' : 0x03030,
	                      'd7' : 0x030C0,
	                      'd8' : 0x04030,
	                      'd9' : 0x040C0,
	                      'd10': 0x05030,
	                      'd11': 0x050C0,
	                      'd12': 0x06030,
	                      'd13': 0x060C0,
	                      'd14': 0x07030,
	                      'd15': 0x070C0,
	                      'd16': 0x08030,
	                      'd17': 0x080C0,
	                      'd18': 0x09030,
	                      'd19': 0x090C0,
	                      'd20': 0x0A030,
	                      'd21': 0x0A0C0,
	                      'd22': 0x0B030,
	                      'd23': 0x0B0C0,
	                      'd24': 0x0C030,
	                      'd25': 0x0C0C0,
	                      'd26': 0x0D030,
	                      'd27': 0x0D0C0,
	                      'd28': 0x0E030,
	                      'd29': 0x0E0C0,
	                      'd30': 0x0F030,
	                      'd31': 0x0F0C0}

	number_to_name_map = {0x00030: 'd0',
	                      0x000C0: 'd1',
	                      0x01030: 'd2',
	                      0x010C0: 'd3',
	                      0x02030: 'd4',
	                      0x020C0: 'd5',
	                      0x03030: 'd6',
	                      0x030C0: 'd7',
	                      0x04030: 'd8',
	                      0x040C0: 'd9',
	                      0x05030: 'd10',
	                      0x050C0: 'd11',
	                      0x06030: 'd12',
	                      0x060C0: 'd13',
	                      0x07030: 'd14',
	                      0x070C0: 'd15',
	                      0x08030: 'd16',
	                      0x080C0: 'd17',
	                      0x09030: 'd18',
	                      0x090C0: 'd19',
	                      0x0A030: 'd20',
	                      0x0A0C0: 'd21',
	                      0x0B030: 'd22',
	                      0x0B0C0: 'd23',
	                      0x0C030: 'd24',
	                      0x0C0C0: 'd25',
	                      0x0D030: 'd26',
	                      0x0D0C0: 'd27',
	                      0x0E030: 'd28',
	                      0x0E0C0: 'd29',
	                      0x0F030: 'd30',
	                      0x0F0C0: 'd31'}

	def __init__(self, id = None):
		super(DRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_d_register()
			self.type = Register.VFPType
			self.size = 8
		elif isinstance(id, int):
			self.number = id
			self.type = Register.VFPType
			self.size = 8
		elif isinstance(id, str):
			if id in DRegister.name_to_number_map.iterkeys():
				self.number = DRegister.name_to_number_map[id]
				self.type = Register.VFPType
				self.size = 8
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, DRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural D register, nor an id of a virtual register')

	def get_physical_number(self):
		assert not self.is_virtual()
		return {0x00030: 0,
		        0x000C0: 1,
				0x01030: 2,
				0x010C0: 3,
				0x02030: 4,
				0x020C0: 5,
				0x03030: 6,
				0x030C0: 7,
				0x04030: 8,
				0x040C0: 9,
				0x05030: 10,
				0x050C0: 11,
				0x06030: 12,
				0x060C0: 13,
				0x07030: 14,
				0x070C0: 15,
				0x08030: 16,
				0x080C0: 17,
				0x09030: 18,
				0x090C0: 19,
				0x0A030: 20,
				0x0A0C0: 21,
				0x0B030: 22,
				0x0B0C0: 23,
				0x0C030: 24,
				0x0C0C0: 25,
				0x0D030: 26,
				0x0D0C0: 27,
				0x0E030: 28,
				0x0E0C0: 29,
				0x0F030: 30,
				0x0F0C0: 31}[self.number]

	def is_extended(self):
		return self.number >= 0x08000

	def is_compatible_bitboard(self, bitboard):
		if self.get_mask() == 0x300:
			return bitboard in {0x0000000000000003, 0x000000000000000C,
			                    0x0000000000000030, 0x00000000000000C0,
			                    0x0000000000000300, 0x0000000000000C00,
			                    0x0000000000003000, 0x000000000000C000,
			                    0x0000000000030000, 0x00000000000C0000,
			                    0x0000000000300000, 0x0000000000C00000,
			                    0x0000000003000000, 0x000000000C000000,
			                    0x0000000030000000, 0x00000000C0000000,
			                    0x0000000300000000, 0x0000000C00000000,
			                    0x0000003000000000, 0x000000C000000000,
			                    0x0000030000000000, 0x00000C0000000000,
			                    0x0000300000000000, 0x0000C00000000000,
			                    0x0003000000000000, 0x000C000000000000,
			                    0x0030000000000000, 0x00C0000000000000,
			                    0x0300000000000000, 0x0C00000000000000,
			                    0x3000000000000000, 0xC000000000000000}
		elif self.get_mask() == 0x0C0:
			return bitboard in {0x000000000000000C,
			                    0x00000000000000C0,
			                    0x0000000000000C00,
			                    0x000000000000C000,
			                    0x00000000000C0000,
			                    0x0000000000C00000,
			                    0x000000000C000000,
			                    0x00000000C0000000,
			                    0x0000000C00000000,
			                    0x000000C000000000,
			                    0x00000C0000000000,
			                    0x0000C00000000000,
			                    0x000C000000000000,
			                    0x00C0000000000000,
			                    0x0C00000000000000,
			                    0xC000000000000000}
		elif self.get_mask() == 0x030:
			return bitboard in {0x0000000000000003,
			                    0x0000000000000030,
			                    0x0000000000000300,
			                    0x0000000000003000,
			                    0x0000000000030000,
			                    0x0000000000300000,
			                    0x0000000003000000,
			                    0x0000000030000000,
			                    0x0000000300000000,
			                    0x0000003000000000,
			                    0x0000030000000000,
			                    0x0000300000000000,
			                    0x0003000000000000,
			                    0x0030000000000000,
			                    0x0300000000000000,
			                    0x3000000000000000}
		else:
			assert False

	def __str__(self):
		if self.is_virtual():
			return 'd-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return DRegister.number_to_name_map[self.number]

	def __getitem__(self, key):
		import sys
		if isinstance(key, slice) and key.start is None and key.stop is None and key.step is None:
			return DRegisterLanes(self)
		else:
			raise ValueError("Illegal subscript value %s" % key) 

	def get_parent(self):
		if self.get_mask() != 0x300:
			return QRegister(self.number | 0x0F0)

	def get_low_part(self):
		if (self.number & ~0xFFF) == 0x300:
			return SRegister((self.number & ~0xFFF) | 0x100)
		elif (self.number & ~0xFFF) == 0x0C0:
			return SRegister((self.number & ~0xFFF) | 0x040)
		else:
			return SRegister((self.number & ~0xFFF) | 0x010)

	def get_high_part(self):
		if (self.number & ~0xFFF) == 0x300:
			return SRegister((self.number & ~0xFFF) | 0x200)
		elif (self.number & ~0xFFF) == 0x0C0:
			return SRegister((self.number & ~0xFFF) | 0x080)
		else:
			return SRegister((self.number & ~0xFFF) | 0x020)

d0  = DRegister('d0')
d1  = DRegister('d1')
d2  = DRegister('d2')
d3  = DRegister('d3')
d4  = DRegister('d4')
d5  = DRegister('d5')
d6  = DRegister('d6')
d7  = DRegister('d7')
d8  = DRegister('d8')
d9  = DRegister('d9')
d10 = DRegister('d10')
d11 = DRegister('d11')
d12 = DRegister('d12')
d13 = DRegister('d13')
d14 = DRegister('d14')
d15 = DRegister('d15')
d16 = DRegister('d16')
d17 = DRegister('d17')
d18 = DRegister('d18')
d19 = DRegister('d19')
d20 = DRegister('d20')
d21 = DRegister('d21')
d22 = DRegister('d22')
d23 = DRegister('d23')
d24 = DRegister('d24')
d25 = DRegister('d25')
d26 = DRegister('d26')
d27 = DRegister('d27')
d28 = DRegister('d28')
d29 = DRegister('d29')
d30 = DRegister('d30')
d31 = DRegister('d31')

class DRegisterLanes:
	def __init__(self, register):
		if isinstance(register, DRegister):
			self.register = register
		else:
			raise TypeError('Register parameter is not an instance of DRegister')

	def __str__(self):
		return str(self.register) + "[]"

class QRegister(Register):
	name_to_number_map = {'q0' : 0x000F0,
	                      'q1' : 0x010F0,
	                      'q2' : 0x020F0,
	                      'q3' : 0x030F0,
	                      'q4' : 0x040F0,
	                      'q5' : 0x050F0,
	                      'q6' : 0x060F0,
	                      'q7' : 0x070F0,
	                      'q8' : 0x080F0,
	                      'q9' : 0x090F0,
	                      'q10': 0x0A0F0,
	                      'q11': 0x0B0F0,
	                      'q12': 0x0C0F0,
	                      'q13': 0x0D0F0,
	                      'q14': 0x0E0F0,
	                      'q15': 0x0F0F0}

	number_to_name_map = {0x000F0: 'q0',
	                      0x010F0: 'q1',
	                      0x020F0: 'q2',
	                      0x030F0: 'q3',
	                      0x040F0: 'q4',
	                      0x050F0: 'q5',
	                      0x060F0: 'q6',
	                      0x070F0: 'q7',
	                      0x080F0: 'q8',
	                      0x090F0: 'q9',
	                      0x0A0F0: 'q10',
	                      0x0B0F0: 'q11',
	                      0x0C0F0: 'q12',
	                      0x0D0F0: 'q13',
	                      0x0E0F0: 'q14',
	                      0x0F0F0: 'q15'}

	def __init__(self, id = None):
		super(QRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_q_register()
			self.type = Register.VFPType
			self.size = 16
		elif isinstance(id, int):
			self.number = id
			self.type = Register.VFPType
			self.size = 16
		elif isinstance(id, str):
			if id in QRegister.name_to_number_map:
				self.number = QRegister.name_to_number_map[id]
				self.type = Register.VFPType
				self.size = 16
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, QRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural Q register, nor an id of a virtual register')

	def get_physical_number(self):
		assert not self.is_virtual()
		return {0x000F0: 0,
		        0x010F0: 1,
				0x020F0: 2,
				0x030F0: 3,
				0x040F0: 4,
				0x050F0: 5,
				0x060F0: 6,
				0x070F0: 7,
				0x080F0: 8,
				0x090F0: 9,
				0x0A0F0: 10,
				0x0B0F0: 11,
				0x0C0F0: 12,
				0x0D0F0: 13,
				0x0E0F0: 14,
				0x0F0F0: 15}[self.number]

	def is_compatible_bitboard(self, bitboard):
		if self.get_mask() == 0x0F0:
			return bitboard in {0x000000000000000F,
			                    0x00000000000000F0,
			                    0x0000000000000F00,
			                    0x000000000000F000,
			                    0x00000000000F0000,
			                    0x0000000000F00000,
			                    0x000000000F000000,
			                    0x00000000F0000000,
			                    0x0000000F00000000,
			                    0x000000F000000000,
			                    0x00000F0000000000,
			                    0x0000F00000000000,
			                    0x000F000000000000,
			                    0x00F0000000000000,
			                    0x0F00000000000000,
			                    0xF000000000000000}
		else:
			assert False

	def is_extended(self):
		return self.number >= 0x08000

	def __str__(self):
		if self.is_virtual():
			return 'q-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return QRegister.number_to_name_map[self.number]

	def get_low_part(self):
		return DRegister((self.number & ~0xFFF) | 0x030)

	def get_high_part(self):
		return DRegister((self.number & ~0xFFF) | 0x0C0)

q0  = QRegister('q0')
q1  = QRegister('q1')
q2  = QRegister('q2')
q3  = QRegister('q3')
q4  = QRegister('q4')
q5  = QRegister('q5')
q6  = QRegister('q6')
q7  = QRegister('q7')
q8  = QRegister('q8')
q9  = QRegister('q9')
q10 = QRegister('q10')
q11 = QRegister('q11')
q12 = QRegister('q12')
q13 = QRegister('q13')
q14 = QRegister('q14')
q15 = QRegister('q15')

class Operand(object):
	RegisterType = 1
	RegisterListType = 2
	RegisterLanesType = 3
	RegisterLanesListType = 4
	ShiftedRegisterType = 5
	AddressRegisterType = 6
	ImmediateType = 7
	MemoryType = 8
	ConstantType = 9
	VariableType = 10
	LabelType = 11
	NoneType = 12
	
	def __init__(self, operand):
		super(Operand, self).__init__()
		import copy
		if isinstance(operand, GeneralPurposeRegisterWriteback):
			self.type = Operand.AddressRegisterType
			self.register = copy.deepcopy(operand.register)
		elif isinstance(operand, Register):
			self.type = Operand.RegisterType
			self.register = copy.deepcopy(operand)
		elif isinstance(operand, DRegisterLanes):
			self.type = Operand.DRegisterLanesType
			self.lanes = copy.deepcopy(operand)
		elif isinstance(operand, ShiftedGeneralPurposeRegister):
			self.type = Operand.ShiftedRegisterType
			self.register = copy.deepcopy(operand)
		elif isinstance(operand, tuple):
			if all(isinstance(element, Register) for element in operand):
				if len(set((register.type, register.size) for register in operand)) == 1:
					self.type = Operand.RegisterListType
					self.register_list = copy.deepcopy(operand)
				else:
					raise TypeError('Register in the list {0} have different types'.format(", ".join(operand)))
			elif all(isinstance(element, DRegisterLanes) for element in operand):
				self.type = Operand.RegisterLanesListType
				self.register_list = copy.deepcopy(operand)
			else:
				raise TypeError('Unknown tuple elements {0}'.format(operand))
		elif isinstance(operand, int) or isinstance(operand, long):
			if -9223372036854775808L <= operand <= 18446744073709551615L:
				self.type = Operand.ImmediateType
				self.immediate = operand
			else:
				raise ValueError('The immediate operand {0} is not a 64-bit value'.format(operand))
		elif isinstance(operand, list):
			if len(operand) == 1 and (isinstance(operand[0], GeneralPurposeRegister) or isinstance(operand[0], GeneralPurposeRegisterWriteback)):
				self.type = Operand.MemoryType
				self.base = copy.deepcopy(operand[0])
				self.offset = None
			elif len(operand) == 2 and isinstance(operand[0], GeneralPurposeRegister) and isinstance(operand[1], int):
				self.type = Operand.MemoryType
				self.base = copy.deepcopy(operand[0])
				self.offset = operand[1]
			else:
				raise ValueError('Memory operand must be a list with only one or two elements')
		elif isinstance(operand, Constant):
			self.type = Operand.ConstantType
			self.constant = operand
			self.size = operand.size * operand.repeats
		elif isinstance(operand, LocalVariable):
			self.type = Operand.VariableType
			self.variable = operand
			self.size = operand.size * 8
		elif isinstance(operand, str):
			self.type = Operand.LabelType
			self.label = operand
		elif isinstance(operand, Label):
			self.type = Operand.LabelType
			self.label = operand.name
		elif operand is None:
			self.type = Operand.NoneType
		else:
			raise TypeError('The operand {0} is not a valid assembly instruction operand'.format(operand))

	def __str__(self):
		if self.is_constant():
			if self.constant.prefix is None:
				return "[rel {0}]".format(self.constant.label)
			else:
				return "[rel {1}.{0}]".format(self.constant.label, self.constant.prefix)
		elif self.is_local_variable():
			return str(self.variable)
		elif self.is_memory_address():
			if self.offset is None:
				if isinstance(self.base, GeneralPurposeRegisterWriteback):
					return "[" + str(self.base.register) + "]!"
				else:
					return "[" + str(self.base) + "]"
			else:
				if isinstance(self.base, GeneralPurposeRegisterWriteback):
					return "[" + str(self.base.register) + ", #" + str(self.offset) + "]!"
				else:
					return "[" + str(self.base) + ", #" + str(self.offset) + "]"
		elif self.is_register() or self.is_shifted_general_purpose_register():
			return str(self.register)
		elif self.is_register_lanes():
			return str(self.register)
		elif self.is_address_register():
			return str(self.register) + "!"
		elif self.is_register_list() or self.is_register_lanes_list():
			return "{" + ", ".join(map(str, self.register_list)) + "}"
		elif self.is_label():
			return self.label
		elif self.is_immediate():
			return "#" + str(self.immediate)
		elif self.is_none():
			return ""
		else:
			raise TypeError('Unsupported operand type')

	def __eq__(self, other):
		if isinstance(other, Operand) and self.type == other.type:
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

	def __ne__(self, other):
		return not self == other

	def is_none(self):
		return self.type == Operand.NoneType

	def is_immediate(self):
		return self.type == Operand.ImmediateType

	def is_modified_immediate12(self):
		def rotate32(x, n):
			return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF
		
		if self.type == Operand.ImmediateType:
			if -2147483648 <= self.immediate <= 4294967295:
				dword = self.immediate & 0xFFFFFFFF
				ndword = (~self.immediate) & 0xFFFFFFFF
				return any([(rotate32(dword, n) & 0xFFFFFF00) == 0x00000000 or (rotate32(ndword, n) & 0xFFFFFF00) == 0x00000000 for n in range(0, 32, 2)])
			else:
				return False
		else:
			return False
	
	def is_neon_modified_immediate8(self):
		return self.type == Operand.ImmediateType and -128 <= self.immediate <= 255

	def is_neon_modified_immediate16(self):
		if self.type == Operand.ImmediateType and -32768 <= self.immediate <= 65535:
			hword = self.immediate & 0xFFFF
			return (hword & 0xFF00) == 0 or (hword & 0x00FF) == 0
		else:
			return False

	def is_neon_modified_immediate32(self):
		if self.type == Operand.ImmediateType and -2147483648 <= self.immediate <= 4294967295:
			word = self.immediate & 0xFFFFFFFF
			return (word & 0x00FFFFFF) == 0x00000000 or \
			       (word & 0xFF00FFFF) == 0x00000000 or \
			       (word & 0xFFFF00FF) == 0x00000000 or \
			       (word & 0xFFFFFF00) == 0x00000000 or \
			       (word & 0xFF00FFFF) == 0x0000FFFF or \
			       (word & 0xFFFF00FF) == 0x000000FF
		else:
			return False

	def is_neon_modified_immediate64(self): 
		if self.type == Operand.ImmediateType and -2147483648 <= self.immediate <= 4294967295:
			dword = self.immediate & 0xFFFFFFFFFFFFFFFF
			byte = dword & 0xFF
			return all([(dword >> n) & 0xFF == byte for n in range(8, 64, 8)]) 
		else:
			return False

	def is_preindexed_memory_address(self):
		return self.type == Operand.MemoryType and self.offset is not None and isinstance(self.base, GeneralPurposeRegisterWriteback)

	def is_memory_address(self, offset_bits = None, allow_writeback = True):
		if self.type == Operand.MemoryType:
			if not allow_writeback and isinstance(self.base, GeneralPurposeRegisterWriteback):
				return False
			else:
				if self.offset is None or offset_bits is None:
					return True
				else:
					bound = (1 << offset_bits) - 1
					return -bound <= self.offset <= bound
		else:
			return False

	def is_writeback_memory_address(self):
		return self.type == Operand.MemoryType and isinstance(self.base, GeneralPurposeRegisterWriteback)

	def is_memory_address_offset8_mod4(self):
		return self.type == Operand.MemoryType and (self.offset is None or -1020 <= self.offset <= 1020 and self.offset % 4 == 0)

	def is_offset8(self):
		return self.type == Operand.ImmediateType and -255 <= self.immediate <= 255
	
	def is_offset12(self):
		return self.type == Operand.ImmediateType and -4095 <= self.immediate <= 4095 

	def is_label(self):
		return self.type == Operand.LabelType

	def is_constant(self):
		return self.type == Operand.ConstantType

	def is_local_variable(self):
		return self.type == Operand.VariableType

	def is_register(self):
		return self.type == Operand.RegisterType
	
	def is_register_lanes(self):
		return self.type == Operand.RegisterLanesType
	
	def is_register_list(self):
		return self.is_register() or self.type == Operand.RegisterListType

	def is_register_lanes_list(self):
		return self.type == Operand.RegisterLanesListType

	def is_general_purpose_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, GeneralPurposeRegister)

	def is_shifted_general_purpose_register(self):
		return self.is_general_purpose_register() or self.type == Operand.ShiftedRegisterType and isinstance(self.register, ShiftedGeneralPurposeRegister)

	def is_general_purpose_register_list(self):
		return self.is_general_purpose_register() or self.type == Operand.RegisterListType and isinstance(self.register_list[0], GeneralPurposeRegister)

	def is_address_register(self):
		return self.is_general_purpose_register() or self.type == Operand.AddressRegisterType

	def is_wmmx_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, WMMXRegister)

	def is_s_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, SRegister)

	def is_s_register_list(self):
		return self.is_s_register() or self.type == Operand.RegisterListType and isinstance(self.register_list[0], SRegister)

	def is_d_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, DRegister)

	def is_d_register_list(self):
		return self.is_d_register() or self.type == Operand.RegisterListType and isinstance(self.register_list[0], DRegister)

	def is_q_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, QRegister)

	def is_vldst1_register_list(self):
		return self.is_d_register() or self.type == Operand.RegisterListType and isinstance(self.register_list[0], DRegister) and len(self.register_list) <= 4

	def is_vldst1_register_lanes_list(self):
		return self.type == Operand.RegisterLanesType and isinstance(self.register, DRegisterLanes) or \
			self.type == Operand.RegisterLanesListType and all(isinstance(register, DRegisterLanes) for register in self.register_list)

	def is_general_purpose_memory_address(self):
		return self.type == Operand.MemoryType and -4095 <= self.offset <= 4095 

	def get_registers_list(self):
		if self.is_address_register() or self.is_register() or self.is_register_lanes():
			return [self.register]
		elif self.is_shifted_general_purpose_register():
			return [self.register.register]
		elif self.is_constant():
			return list()
		elif self.is_local_variable():
			return [rsp]
		elif self.is_register_list():
			return list(self.register_list)
		elif self.is_register_lanes_list():
			return [register_lanes.register for register_lanes in self.register_list]
		elif self.is_memory_address():
			if isinstance(self.base, GeneralPurposeRegisterWriteback):
				return [self.base.register]
			else:
				return [self.base]
		else:
			return list()

	def get_writeback_registers_list(self):
		if self.is_memory_address():
			if isinstance(self.base, GeneralPurposeRegisterWriteback):
				return [self.base.register]
			else:
				return [self.base]
		else:
			return list()

class QuasiInstruction(object):
	def __init__(self, name, origin = None):
		super(QuasiInstruction, self).__init__()
		self.name = name
		self.line_number = origin[1][2] if origin else None
		self.source_file = origin[1][1] if origin else None
		self.source_code = origin[1][4][0].strip() if origin else None

class Instruction(QuasiInstruction):
	def __init__(self, name, operands, isa_extension = None, origin = None):
		super(Instruction, self).__init__(name, origin = origin)
		if(not isa_extension is None) and (not isa_extension in supported_isa_extensions):
			raise ValueError('Instruction ISA extension {0} in not in the supported ISA extensions list ({1})'.format(isa_extension, ", ".join(supported_isa_extensions)))
		self.operands = operands
		self.isa_extension = isa_extension
		self.available_registers = set()
		self.live_registers = set()

	def __len__(self):
		return self.size

	def __str__(self):
		return self.name + " " + ", ".join(map(str, self.operands))

	def get_isa_extension(self):
		return self.isa_extension

	def get_registers_list(self):
		return [register for operand in self.operands for register in operand.get_registers_list()]

	def get_local_variable(self):
		for operand in self.operands:
			if isinstance(operand, Operand) and operand.is_local_variable():
				return operand.variable

	def get_constant(self):
		for operand in self.operands:
			if isinstance(operand, Operand) and operand.is_constant():
				return operand.constant

class Label(object):
	def __init__(self, name):
		super(Label, self).__init__()
		self.name = name

	def __str__(self):
		return "<LABEL:" + self.name + '>'

class LabelMark(QuasiInstruction):
	def __init__(self, name, origin = None):
		super(LabelMark, self).__init__('<LABEL>', origin = origin)
		if name.is_label():
			self.name = name.label
		else:
			raise TypeError("Name must be an Label or string")
		self.input_branches = set()

	def __str__(self):
		return "L" + self.name + ':'

class AlignQuasiInstruction(QuasiInstruction):
	supported_alignments = [2, 4, 8, 16, 32]

	def __init__(self, alignment, origin = None):
		super(AlignQuasiInstruction, self).__init__('<ALIGN>', origin = origin)
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
	def __init__(self, destination, source, origin = None):
		super(LoadConstantPseudoInstruction, self).__init__('<LOAD-CONSTANT>', origin = origin)
		if destination.is_register():
			self.destination = destination
		else:
			raise ValueError('Load constant pseudo-instruction expects a register as a destination')
		if source.is_constant():
			if destination.register.size * 8 == source.constant.size * source.constant.repeats:
				self.source = source
			elif destination.register.size == 16 and source.constant.size == 64 and source.constant.repeats == 1 and source.constant.basic_type == 'float64':
				self.source = source
			elif destination.register.size == 16 and source.constant.size == 32 and source.constant.repeats == 1 and source.constant.basic_type == 'float32':
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

	def get_constant(self):
		return self.source.constant

	def get_local_variable(self):
		return None

class LoadParameterPseudoInstruction(Instruction):
	def __init__(self, destination, source, origin = None):
		super(LoadParameterPseudoInstruction, self).__init__('<LOAD-PARAMETER>', [destination, source], origin = origin)
		if destination.is_general_purpose_register():
			self.destination = destination
		else:
			raise ValueError('Load parameter pseudo-instruction expects a general-purpose 64-bit register as a destination')
		if isinstance(source, peachpy.c.Parameter):
			parameter = current_function.find_parameter(source)
			if parameter is not None:
				self.parameter = parameter
			else:
				raise ValueError('{0} is not an argument of the currently active function'.format(source))
		else:
			raise TypeError('Load parameter pseudo-instruction expects a Parameter object as a source')
		# MOV r64/m64, r64: 8B /r
		self.size = 1 + 2 + 1 + 1 # REX prefix + 1-byte opcode + ModR/M + SIB (rsp addressing) + 8-bit offset

	def __str__(self):
		return "LOAD.PARAMETER {0} = {1}".format(self.destination, self.parameter)

	def get_input_registers_list(self):
		if self.parameter.register:
			return [self.parameter.register]
		else:
			return [sp]

	def get_output_registers_list(self):
		return [self.destination.register]

class AssumeInitializedPseudoInstruction(Instruction):
	def __init__(self, destination, origin = None):
		super(AssumeInitializedPseudoInstruction, self).__init__('<ASSUME-INITIALIZED>', origin = origin)
		if destination.is_register():
			self.destination = destination
		else:
			raise ValueError('Assume initialized pseudo-instruction expects a register as a destination')
		self.size = 0

	def __str__(self):
		return "ASSUME.INITIALIZED {0}".format(self.destination)

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class ArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['ADD', 'ADDEQ', 'ADDNE', 'ADDCS', 'ADDHS', 'ADDCC', 'ADDLO', 'ADDMI', 'ADDPL', 'ADDVS', 'ADDVC', 'ADDHI', 'ADDLS', 'ADDGE', 'ADDLT', 'ADDGT', 'ADDLE',
		                        'ADDS', 'ADDSEQ', 'ADDSNE', 'ADDSCS', 'ADDSHS', 'ADDSCC', 'ADDSLO', 'ADDSMI', 'ADDSPL', 'ADDSVS', 'ADDSVC', 'ADDSHI', 'ADDSLS', 'ADDSGE', 'ADDSLT', 'ADDSGT', 'ADDSLE',
		                        'ADC', 'ADCEQ', 'ADCNE', 'ADCCS', 'ADCHS', 'ADCCC', 'ADCLO', 'ADCMI', 'ADCPL', 'ADCVS', 'ADCVC', 'ADCHI', 'ADCLS', 'ADCGE', 'ADCLT', 'ADCGT', 'ADCLE',
		                        'ADCS', 'ADCSEQ', 'ADCSNE', 'ADCSCS', 'ADCSHS', 'ADCSCC', 'ADCSLO', 'ADCSMI', 'ADCSPL', 'ADCSVS', 'ADCSVC', 'ADCSHI', 'ADCSLS', 'ADCSGE', 'ADCSLT', 'ADCSGT', 'ADCSLE',
		                        'SUB', 'SUBEQ', 'SUBNE', 'SUBCS', 'SUBHS', 'SUBCC', 'SUBLO', 'SUBMI', 'SUBPL', 'SUBVS', 'SUBVC', 'SUBHI', 'SUBLS', 'SUBGE', 'SUBLT', 'SUBGT', 'SUBLE',
		                        'SUBS', 'SUBSEQ', 'SUBSNE', 'SUBSCS', 'SUBSHS', 'SUBSCC', 'SUBSLO', 'SUBSMI', 'SUBSPL', 'SUBSVS', 'SUBSVC', 'SUBSHI', 'SUBSLS', 'SUBSGE', 'SUBSLT', 'SUBSGT', 'SUBSLE',
		                        'SBC', 'SBCEQ', 'SBCNE', 'SBCCS', 'SBCHS', 'SBCCC', 'SBCLO', 'SBCMI', 'SBCPL', 'SBCVS', 'SBCVC', 'SBCHI', 'SBCLS', 'SBCGE', 'SBCLT', 'SBCGT', 'SBCLE',
		                        'SBCS', 'SBCSEQ', 'SBCSNE', 'SBCSCS', 'SBCSHS', 'SBCSCC', 'SBCSLO', 'SBCSMI', 'SBCSPL', 'SBCSVS', 'SBCSVC', 'SBCSHI', 'SBCSLS', 'SBCSGE', 'SBCSLT', 'SBCSGT', 'SBCSLE',
		                        'RSB', 'RSBEQ', 'RSBNE', 'RSBCS', 'RSBHS', 'RSBCC', 'RSBLO', 'RSBMI', 'RSBPL', 'RSBVS', 'RSBVC', 'RSBHI', 'RSBLS', 'RSBGE', 'RSBLT', 'RSBGT', 'RSBLE',
		                        'RSBS', 'RSBSEQ', 'RSBSNE', 'RSBSCS', 'RSBSHS', 'RSBSCC', 'RSBSLO', 'RSBSMI', 'RSBSPL', 'RSBSVS', 'RSBSVC', 'RSBSHI', 'RSBSLS', 'RSBSGE', 'RSBSLT', 'RSBSGT', 'RSBSLE',
		                        'RSC', 'RSCEQ', 'RSCNE', 'RSCCS', 'RSCHS', 'RSCCC', 'RSCLO', 'RSCMI', 'RSCPL', 'RSCVS', 'RSCVC', 'RSCHI', 'RSCLS', 'RSCGE', 'RSCLT', 'RSCGT', 'RSCLE',
		                        'RSCS', 'RSCSEQ', 'RSCSNE', 'RSCSCS', 'RSCSHS', 'RSCSCC', 'RSCSLO', 'RSCSMI', 'RSCSPL', 'RSCSVS', 'RSCSVC', 'RSCSHI', 'RSCSLS', 'RSCSGE', 'RSCSLT', 'RSCSGT', 'RSCSLE',
		                        'AND', 'ANDEQ', 'ANDNE', 'ANDCS', 'ANDHS', 'ANDCC', 'ANDLO', 'ANDMI', 'ANDPL', 'ANDVS', 'ANDVC', 'ANDHI', 'ANDLS', 'ANDGE', 'ANDLT', 'ANDGT', 'ANDLE',
		                        'ANDS', 'ANDSEQ', 'ANDSNE', 'ANDSCS', 'ANDSHS', 'ANDSCC', 'ANDSLO', 'ANDSMI', 'ANDSPL', 'ANDSVS', 'ANDSVC', 'ANDSHI', 'ANDSLS', 'ANDSGE', 'ANDSLT', 'ANDSGT', 'ANDSLE',
		                        'BIC', 'BICEQ', 'BICNE', 'BICCS', 'BICHS', 'BICCC', 'BICLO', 'BICMI', 'BICPL', 'BICVS', 'BICVC', 'BICHI', 'BICLS', 'BICGE', 'BICLT', 'BICGT', 'BICLE',
		                        'BICS', 'BICSEQ', 'BICSNE', 'BICSCS', 'BICSHS', 'BICSCC', 'BICSLO', 'BICSMI', 'BICSPL', 'BICSVS', 'BICSVC', 'BICSHI', 'BICSLS', 'BICSGE', 'BICSLT', 'BICSGT', 'BICSLE',
		                        'ORR', 'ORREQ', 'ORRNE', 'ORRCS', 'ORRHS', 'ORRCC', 'ORRLO', 'ORRMI', 'ORRPL', 'ORRVS', 'ORRVC', 'ORRHI', 'ORRLS', 'ORRGE', 'ORRLT', 'ORRGT', 'ORRLE',
		                        'ORRS', 'ORRSEQ', 'ORRSNE', 'ORRSCS', 'ORRSHS', 'ORRSCC', 'ORRSLO', 'ORRSMI', 'ORRSPL', 'ORRSVS', 'ORRSVC', 'ORRSHI', 'ORRSLS', 'ORRSGE', 'ORRSLT', 'ORRSGT', 'ORRSLE',
		                        'EOR', 'EOREQ', 'EORNE', 'EORCS', 'EORHS', 'EORCC', 'EORLO', 'EORMI', 'EORPL', 'EORVS', 'EORVC', 'EORHI', 'EORLS', 'EORGE', 'EORLT', 'EORGT', 'EORLE',
		                        'EORS', 'EORSEQ', 'EORSNE', 'EORSCS', 'EORSHS', 'EORSCC', 'EORSLO', 'EORSMI', 'EORSPL', 'EORSVS', 'EORSVC', 'EORSHI', 'EORSLS', 'EORSGE', 'EORSLT', 'EORSGT', 'EORSLE']
		super(ArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], origin = origin)
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register() and source_x.is_general_purpose_register() and source_y.is_modified_immediate12():
			pass
		elif destination.is_general_purpose_register() and source_x.is_general_purpose_register() and source_y.is_shifted_general_purpose_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class CompareInstruction(Instruction):
	def __init__(self, name, source_x, source_y, origin = None):
		allowed_instructions = ['CMP', 'CMPEQ', 'CMPNE', 'CMPCS', 'CMPHS', 'CMPCC', 'CMPLO', 'CMPMI', 'CMPPL', 'CMPVS', 'CMPVC', 'CMPHI', 'CMPLS', 'CMPGE', 'CMPLT', 'CMPGT', 'CMPLE',
		                        'TEQ', 'TEQEQ', 'TEQNE', 'TEQCS', 'TEQHS', 'TEQCC', 'TEQLO', 'TEQMI', 'TEQPL', 'TEQVS', 'TEQVC', 'TEQHI', 'TEQLS', 'TEQGE', 'TEQLT', 'TEQGT', 'TEQLE',
		                        'TST', 'TSTEQ', 'TSTNE', 'TSTCS', 'TSTHS', 'TSTCC', 'TSTLO', 'TSTMI', 'TSTPL', 'TSTVS', 'TSTVC', 'TSTHI', 'TSTLS', 'TSTGE', 'TSTLT', 'TSTGT', 'TSTLE',
		                        'TEQ', 'TEQEQ', 'TEQNE', 'TEQCS', 'TEQHS', 'TEQCC', 'TEQLO', 'TEQMI', 'TEQPL', 'TEQVS', 'TEQVC', 'TEQHI', 'TEQLS', 'TEQGE', 'TEQLT', 'TEQGT', 'TEQLE']
		if name in allowed_instructions:
			super(CompareInstruction, self).__init__(name, [source_x, source_y], origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if source_x.is_general_purpose_register() and source_y.is_modified_immediate12():
			pass
		elif source_x.is_general_purpose_register() and source_y.is_general_purpose_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[0].get_registers_list() + self.operands[1].get_registers_list()

	def get_output_registers_list(self):
		return list()

class MovInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = ['MOV', 'MOVEQ', 'MOVNE', 'MOVCS', 'MOVHS', 'MOVCC', 'MOVLO', 'MOVMI', 'MOVPL', 'MOVVS', 'MOVVC', 'MOVHI', 'MOVLS', 'MOVGE', 'MOVLT', 'MOVGT', 'MOVLE',
		                        'MOVS', 'MOVSEQ', 'MOVSNE', 'MOVSCS', 'MOVSHS', 'MOVSCC', 'MOVSLO', 'MOVSMI', 'MOVSPL', 'MOVSVS', 'MOVSVC', 'MOVSHI', 'MOVSLS', 'MOVSGE', 'MOVSLT', 'MOVSGT', 'MOVSLE']
		if name in allowed_instructions:
			super(MovInstruction, self).__init__(name, [destination, source], origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register() and source.is_modified_immediate12():
			pass
		elif destination.is_general_purpose_register() and source.is_general_purpose_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class LoadStoreInstruction(Instruction):
	load_instructions  = ['LDR', 'LDRH', 'LDRSH', 'LDRB', 'LDRSB']
	store_instructions = ['STR', 'STRB', 'STRH']

	def __init__(self, name, register, address, increment, origin = None):
		allowed_instructions = LoadStoreInstruction.load_instructions + LoadStoreInstruction.store_instructions
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if register.is_general_purpose_register() and address.is_memory_address(offset_bits = 8) and increment.is_none():
			super(LoadStoreInstruction, self).__init__(name, [register, address], origin = origin)
		elif name in {'STR', 'LDR', 'LDRB', 'STRB'} and register.is_general_purpose_register() and address.is_memory_address(offset_bits = 12) and increment.is_none():
			super(LoadStoreInstruction, self).__init__(name, [register, address], origin = origin)
		elif register.is_general_purpose_register() and address.is_memory_address(offset_bits = 0, allow_writeback = False) and increment.is_offset8():
			super(LoadStoreInstruction, self).__init__(name, [register, address, increment], origin = origin)
		elif register.is_general_purpose_register() and address.is_memory_address(offset_bits = 0, allow_writeback = False) and increment.is_offset12():
			super(LoadStoreInstruction, self).__init__(name, [register, address, increment], origin = origin)
		else:
			if increment.is_none():
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, register, address))
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, register, address, increment))

	def get_input_registers_list(self):
		input_registers_list = self.operands[0].get_registers_list() if self.name in LoadStoreInstruction.store_instructions else list()
		for operand in self.operands[1:]:
			input_registers_list += operand.get_registers_list()
		return input_registers_list

	def get_output_registers_list(self):
		output_registers_list = self.operands[0].get_registers_list() if self.name in LoadStoreInstruction.load_instructions else list()
		if len(self.operands) > 2 or self.operands[1].is_preindexed_memory_address():
			output_registers_list.append(self.operands[1].base)
		return output_registers_list

class PushPopInstruction(Instruction):
	def __init__(self, name, register_list, origin = None):
		allowed_instructions = {'PUSH', 'POP'}
		if name in allowed_instructions:
			super(PushPopInstruction, self).__init__(name, [register_list], origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if register_list.is_general_purpose_register_list():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format(name, register_list))

	def get_input_registers_list(self):
		if self.name == 'PUSH':
			return self.operands[0].get_registers_list()
		else:
			return list()

	def get_output_registers_list(self):
		if self.name == 'POP':
			return self.operands[0].get_registers_list()
		else:
			return list()

class VFPLoadStoreInstruction(Instruction):
	def __init__(self, name, register, address, origin = None):
		allowed_instructions = {'VLDR', 'VSTR'}
		if name in allowed_instructions:
			super(VFPLoadStoreInstruction, self).__init__(name, [register, address], isa_extension = 'VFP2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if (register.is_d_register() or register.is_s_register()) and address.is_memory_address_offset8_mod4():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, register, address))

	def get_input_registers_list(self):
		input_registers_list = self.operands[1].get_registers_list()
		if self.name == 'VSTR':
			input_registers_list += self.operands[0].get_registers_list()
		return input_registers_list

	def get_output_registers_list(self):
		if self.name == 'VLDR':
			return self.operands[0].get_registers_list()
		else:
			return list()

class VFPLoadStoreMultipleInstruction(Instruction):
	load_instructions = {"VLDM", "VLDMIA", "VLDMDB"}
	store_instructions = {"VSTM", "VSTMIA", "VSTMDB"}

	def __init__(self, name, address, register_list, origin = None):
		if name in VFPLoadStoreMultipleInstruction.load_instructions or name in VFPLoadStoreMultipleInstruction.store_instructions:
			super(VFPLoadStoreMultipleInstruction, self).__init__(name, [address, register_list], isa_extension = 'VFP2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if address.is_address_register() and register_list.is_d_register_list():
			pass
		elif address.is_address_register() and register_list.is_s_register_list():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, register_list, address))

	def get_input_registers_list(self):
		if self.name in VFPLoadStoreMultipleInstruction.store_instructions:
			return self.operands[0].get_registers_list() + self.operands[1].get_registers_list()
		else:
			return self.operands[0].get_registers_list()

	def get_output_registers_list(self):
		if self.name in VFPLoadStoreMultipleInstruction.load_instructions:
			return self.operands[1].get_registers_list()
		else:
			return list()

class NeonLoadStoreInstruction(Instruction):
	load_instructions = {"VLD1.8", "VLD1.16", "VLD1.32", "VLD1.64"}
	store_instructions = {"VST1.8", "VST1.16", "VST1.32", "VST1.64"}

	def __init__(self, name, register_list, address, increment, origin = None):
		if name not in NeonLoadStoreInstruction.load_instructions and name not in NeonLoadStoreInstruction.store_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if register_list.is_vldst1_register_list() and address.is_memory_address(offset_bits = 0) and increment.is_none(): 
			super(NeonLoadStoreInstruction, self).__init__(name, [register_list, address], isa_extension = 'NEON', origin = origin)
		elif register_list.is_vldst1_register_list() and address.is_memory_address(offset_bits = 0, allow_writeback = False) and increment.is_general_purpose_register(): 
			super(NeonLoadStoreInstruction, self).__init__(name, [register_list, address, increment], isa_extension = 'NEON', origin = origin)
		elif register_list.is_vldst1_register_lanes_list() and address.is_memory_address(offset_bits = 0) and increment.is_none():
			super(NeonLoadStoreInstruction, self).__init__(name, [register_list, address], isa_extension = 'NEON', origin = origin)
		elif register_list.is_vldst1_register_lanes_list() and address.is_memory_address(offset_bits = 0, allow_writeback = False) and increment.is_general_purpose_register():
			super(NeonLoadStoreInstruction, self).__init__(name, [register_list, address, increment], isa_extension = 'NEON', origin = origin)
		else:
			if increment.is_none():
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, register_list, address))
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, register_list, address, increment))

	def get_input_registers_list(self):
		input_registers_list = self.operands[1].get_registers_list()
		if self.name in NeonLoadStoreInstruction.store_instructions:
			input_registers_list += self.operands[0].get_registers_list()
		if len(self.operands) == 3:
			input_registers_list += self.operands[2].get_registers_list()
		return input_registers_list 

	def get_output_registers_list(self):
		output_registers_list = list()
		if self.name in NeonLoadStoreInstruction.load_instructions:
			output_registers_list += self.operands[0].get_registers_list()
		if len(self.operands) == 3 or self.operands[1].is_writeback_memory_address():
			output_registers_list += self.operands[1].get_writeback_registers_list()
		return output_registers_list

class VFPPushPopInstruction(Instruction):
	def __init__(self, name, register_list, origin = None):
		allowed_instructions = {'VPUSH', 'VPOP'}
		if name in allowed_instructions:
			super(VFPPushPopInstruction, self).__init__(name, [register_list], isa_extension = 'VFP2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if register_list.is_d_register_list():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format(name, register_list))

	def get_input_registers_list(self):
		if self.name == 'VPUSH':
			return self.operands[0].get_registers_list()
		else:
			return list()

	def get_output_registers_list(self):
		if self.name == 'VPOP':
			return self.operands[0].get_registers_list()
		else:
			return list()

class VFPDoublePrecisionMultiplyAddInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		mla_instructions = ['VMLA.F64', 'VMLS.F64', 'VNMLA.F64', 'VNMLS.F64']
		fma_instructions = ['VFMA.F64', 'VFMS.F64', 'VFNMA.F64', 'VFNMS.F64']
		if name in mla_instructions:
			super(VFPDoublePrecisionMultiplyAddInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP2', origin = origin)
		elif name in fma_instructions:
			super(VFPDoublePrecisionMultiplyAddInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP4', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if destination.is_d_register() and source_x.is_d_register() and source_y.is_d_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[0].get_registers_list() + self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VFPSinglePrecisionMultiplyAddInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		mla_instructions = ['VNMLA.F32', 'VNMLS.F32']
		fma_instructions = ['VFNMA.F32', 'VFNMS.F32']
		if name in mla_instructions:
			super(VFPDoublePrecisionMultiplyAddInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP2', origin = origin)
		elif name in fma_instructions:
			super(VFPDoublePrecisionMultiplyAddInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP4', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(mla_instructions + fma_instructions))
		if destination.is_s_register() and source_x.is_s_register() and source_y.is_s_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[0].get_registers_list() + self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VFPNeonBinaryArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VADD.F32', 'VSUB.F32', 'VMUL.F32']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_s_register() and source_x.is_s_register() and source_y.is_s_register():
			super(VFPNeonBinaryArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP2', origin = origin)
		elif destination.is_d_register() and source_x.is_d_register() and source_y.is_d_register():
			super(VFPNeonBinaryArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'NEON', origin = origin)
		elif destination.is_q_register() and source_x.is_q_register() and source_y.is_q_register():
			super(VFPNeonBinaryArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'NEON', origin = origin)
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VFPNeonMultiplyAddInstruction(Instruction):
	def __init__(self, name, accumulator, factor_x, factor_y, origin = None):
		mla_instructions = ['VMLA.F32', 'VMLS.F32']
		fma_instructions = ['VFMA.F32', 'VFMS.F32']
		if name not in mla_instructions and name not in fma_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if name in mla_instructions and accumulator.is_s_register() and factor_x.is_s_register() and factor_y.is_s_register():
			super(VFPNeonMultiplyAddInstruction, self).__init__(name, [accumulator, factor_x, factor_y], isa_extension = 'VFP2', origin = origin)
		elif name in fma_instructions and accumulator.is_s_register() and factor_x.is_s_register() and factor_y.is_s_register():
			super(VFPNeonMultiplyAddInstruction, self).__init__(name, [accumulator, factor_x, factor_y], isa_extension = 'VFP4', origin = origin)
		elif name in mla_instructions and accumulator.is_d_register() and factor_x.is_d_register() and factor_y.is_d_register():
			super(VFPNeonMultiplyAddInstruction, self).__init__(name, [accumulator, factor_x, factor_y], isa_extension = 'NEON', origin = origin)
		elif name in mla_instructions and accumulator.is_q_register() and factor_x.is_q_register() and factor_y.is_q_register():
			super(VFPNeonMultiplyAddInstruction, self).__init__(name, [accumulator, factor_x, factor_y], isa_extension = 'NEON', origin = origin)
		elif name in fma_instructions and accumulator.is_d_register() and factor_x.is_d_register() and factor_y.is_d_register():
			super(VFPNeonMultiplyAddInstruction, self).__init__(name, [accumulator, factor_x, factor_y], isa_extension = 'NEON2', origin = origin)
		elif name in fma_instructions and accumulator.is_q_register() and factor_x.is_q_register() and factor_y.is_q_register():
			super(VFPNeonMultiplyAddInstruction, self).__init__(name, [accumulator, factor_x, factor_y], isa_extension = 'NEON2', origin = origin)
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[0].get_registers_list() + self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VFPSinglePrecisionBinaryArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VNMUL.F32', 'VDIV.F32']
		super(VFPDoublePrecisionBinaryArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP2', origin = origin)
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_d_register() and source_x.is_s_register() and source_y.is_s_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VFPDoublePrecisionBinaryArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VADD.F64', 'VSUB.F64', 'VMUL.F64', 'VNMUL.F32', 'VNMUL.F64', 'VDIV.F32', 'VDIV.F64']
		super(VFPDoublePrecisionBinaryArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'VFP2', origin = origin)
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_d_register() and source_x.is_d_register() and source_y.is_d_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VFPDoublePrecisionUnaryArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = ['VABS.F64', 'VNEG.F64', 'VSQRT.F64']
		super(VFPDoublePrecisionUnaryArithmeticInstruction, self).__init__(name, [destination, source], isa_extension = 'VFP2', origin = origin)
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_d_register() and source.is_d_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class NeonArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VADD.I8', 'VADD.I16', 'VADD.I32', 'VADD.I64',
		                        'VSUB.I8', 'VSUB.I16', 'VSUB.I32', 'VSUB.I64',
		                        'VMUL.I8', 'VMUL.I16', 'VMUL.I32',
		                        'VMIN.S8', 'VMIN.S16', 'VMIN.S32', 'VMIN.U8', 'VMIN.U16', 'VMIN.U32', 'VMIN.F32',
		                        'VMAX.S8', 'VMAX.S16', 'VMAX.S32', 'VMAX.U8', 'VMAX.U16', 'VMAX.U32', 'VMAX.F32',
		                        'VABD.S8', 'VABD.S16', 'VABD.S32', 'VABD.U8', 'VABD.U16', 'VABD.U32', 'VABD.F32',
		                        'VACGE.F32', 'VACGT.F32', 'VACLE.F32', 'VACLT.F32', 
		                        'VEOR', 'VORR', 'VORN', 'VAND', 'VBIC',
		                        'VPADD.I8', 'VPADD.I16', 'VPADD.I32', 'VPADD.F32',
		                        'VPMIN.S8', 'VPMIN.S16', 'VPMIN.S32', 'VPMIN.U8', 'VPMIN.U16', 'VPMIN.U32', 'VPMIN.F32',
		                        'VPMAX.S8', 'VPMAX.S16', 'VPMAX.S32', 'VPMAX.U8', 'VPMAX.U16', 'VPMAX.U32', 'VPMAX.F32',
		                        'VQADD.S8', 'VQADD.S16', 'VQADD.S32', 'VQADD.S64', 'VQADD.U8', 'VQADD.U16', 'VQADD.U32', 'VQADD.U64',
		                        'VQSUB.S8', 'VQSUB.S16', 'VQSUB.S32', 'VQSUB.S64', 'VQSUB.U8', 'VQSUB.U16', 'VQSUB.U32', 'VQSUB.U64',
		                        'VHADD.S8', 'VHADD.S16', 'VHADD.S32', 'VHADD.U8', 'VHADD.U16', 'VHADD.U32',
		                        'VHSUB.S8', 'VHSUB.S16', 'VHSUB.S32', 'VHSUB.U8', 'VHSUB.U16', 'VHSUB.U32',
		                        'VRHADD.S8', 'VRHADD.S16', 'VRHADD.S32', 'VRHADD.U8', 'VRHADD.U16', 'VRHADD.U32',
		                        'VRECPS.F32', 'VRSQRTS.F32',
		                        'VTST.8', 'VTST.16', 'VTST.32']
		super(NeonArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'NEON', origin = origin)
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_d_register() and source_x.is_d_register() and source_y.is_d_register():
			pass
		elif destination.is_q_register() and source_x.is_q_register() and source_y.is_q_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class NeonWideArithmeticInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VADDL.S8', 'VADDL.S16', 'VADDL.S32',
		                        'VADDL.U8', 'VADDL.U16', 'VADDL.U32',
		                        'VSUBL.S8', 'VSUBL.S16', 'VSUBL.S32',
		                        'VSUBL.U8', 'VSUBL.U16', 'VSUBL.U32',
		                        'VMULL.S8', 'VMULL.S16', 'VMULL.S32',
		                        'VMULL.U8', 'VMULL.U16', 'VMULL.U32',
		                        'VMULL.P8']
		super(NeonWideArithmeticInstruction, self).__init__(name, [destination, source_x, source_y], isa_extension = 'NEON', origin = origin)
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_q_register() and source_x.is_d_register() and source_y.is_d_register():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list() + self.operands[2].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class VfpNeonMovInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = {'VMOV', 'VMOV.F32', 'VMOV.F64'}
		if name == 'VMOV' and destination.is_q_register() and source.is_q_register():
			super(VfpNeonMovInstruction, self).__init__(name, [destination, source], isa_extension = 'NEON', origin = origin)
		elif name == 'VMOV' and destination.is_d_register() and source.is_d_register():
			super(VfpNeonMovInstruction, self).__init__(name, [destination, source], isa_extension = 'NEON', origin = origin)
		elif name == 'VMOV.F32' and destination.is_s_register() and source.is_s_register():
			super(VfpNeonMovInstruction, self).__init__(name, [destination, source], isa_extension = 'VFP2', origin = origin)
		elif name == 'VMOV.F64' and destination.is_d_register() and source.is_d_register():
			super(VfpNeonMovInstruction, self).__init__(name, [destination, source], isa_extension = 'VFP2', origin = origin)
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.operands[1].get_registers_list()

	def get_output_registers_list(self):
		return self.operands[0].get_registers_list()

class BranchInstruction(Instruction):
	def __init__(self, name, destination, origin = None):
		allowed_instructions = {'B', 'BEQ', 'BNE', 'BCS', 'BHS', 'BCC', 'BLO', 'BMI', 'BPL', 'BVS', 'BVC', 'BHI', 'BLS', 'BGE', 'BLT', 'BGT', 'BLE'}
		if name in allowed_instructions:
			super(BranchInstruction, self).__init__(name, [destination], origin = origin)
			self.is_visited = False
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions'.format(name))
		if destination.is_label():
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format('BX', destination))

	def get_input_registers_list(self):
		return self.operands[0].get_registers_list()

	def get_output_registers_list(self):
		return list()

	def is_conditional(self):
		return not self.name == 'B'

	def __str__(self):
		return self.name + " L" + str(self.operands[0])

class BranchExchangeInstruction(Instruction):
	def __init__(self, destination, origin = None):
		super(BranchExchangeInstruction, self).__init__('BX', [destination], origin = origin)
		if destination.is_general_purpose_register() and destination.register == lr:
			pass
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format('BX', destination))

	def get_input_registers_list(self):
		return self.operands[0].get_registers_list()

	def get_output_registers_list(self):
		return list()

class ReturnInstruction(QuasiInstruction):
	def __init__(self, return_value = None, origin = None):
		super(ReturnInstruction, self).__init__('RETURN', origin = origin)
		if return_value.is_none():
			self.return_value = None
		elif return_value.is_modified_immediate12():
			self.return_value = return_value.immediate
		else:
			raise ValueError('Return value is not representable as a 12-bit modified immediate integer')

	def to_instruction_list(self):
		return_instructions = InstructionStream()
		with return_instructions:
	 		if self.return_value is None:
	 			pass
	 		else:
	 			MOV( r0, self.return_value )
		 	BX( lr )
		return list(iter(return_instructions))

	def __str__(self):
		return "RETURN {0}".format(self.return_value)

	def get_input_registers_list(self):
		return [rsp]

	def get_output_registers_list(self):
		return [rsp]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class BreakInstruction(Instruction):
	def __init__(self, origin = None):
		super(BreakInstruction, self).__init__('BKPT', (), origin = origin)

	def __str__(self):
		return "BKPT"

	def get_input_registers_list(self):
		return []

	def get_output_registers_list(self):
		return []

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

def LABEL(name):
	instruction = LabelMark(Operand(name))
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ALIGN(alignment):
	instruction = AlignQuasiInstruction(alignment)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RETURN(return_value = None):
	instruction = ReturnInstruction(Operand(return_value))
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BX(destination):
	instruction = BranchExchangeInstruction(Operand(destination))
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BKPT():
	instruction = BreakInstruction()
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

class LOAD:
	@staticmethod
	def CONSTANT(destination, source):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = LoadConstantPseudoInstruction(Operand(destination), Operand(source), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def PARAMETER(destination, source):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = LoadParameterPseudoInstruction(Operand(destination), source, origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def PARAMETERS():
		origin = inspect.stack() if Function.get_current().collect_origin else None
		registers = list()
		for argument in Function.get_current().arguments:
			if argument.get_type().is_pointer() or (argument.get_type().is_integer() and argument.get_type().get_size(Function.get_current().abi) != 8):
				register = GeneralPurposeRegister()
				LOAD.PARAMETER( register, argument )
			elif argument.get_type().is_floating_point():
				register = SSERegister()
				LOAD.PARAMETER( register, argument )
			else:
				raise TypeError("Unknown argument type %s" % argument.get_type())
			registers.append(register)
		return tuple(registers)

	@staticmethod
	def ZERO(destination, ctype):
		if isinstance(ctype, peachpy.c.Type):
# 			if isinstance(destination, SRegister):
# 				PXOR( destination, destination )
# 			elif isinstance(destination, DRegister):
# 				if ctype.is_floating_point():
# 					if Target.has_avx():
# 						SIMD_XOR = {4: VXORPS, 8: VXORPD }[ctype.get_size()]
# 					else:
# 						SIMD_XOR = {4: XORPS, 8: XORPD}[ctype.get_size()]
# 				else:
# 					SIMD_XOR = VPXOR if Target.has_avx() else PXOR
# 				SIMD_XOR( destination, destination )
# 			elif isinstance(destination, QRegister):
# 				LOAD.ZERO( destination.get_oword(), ctype )
# 			else:
				raise TypeError("Unsupported type of destination register")
		else:
			raise TypeError("Type must be a C type")

	@staticmethod
	def ELEMENT(destination, source, ctype, increment_pointer = False):
		if isinstance(ctype, peachpy.c.Type):
			if Operand(destination).is_register():
				if Operand(source).is_memory_address():
					memory_size = ctype.get_size(current_function.abi)
					if isinstance(destination, GeneralPurposeRegister):
						if ctype.is_unsigned_integer():
							if memory_size == 4:
								if increment_pointer:
									LDR( destination, source, memory_size )
								else:
									LDR( destination, source )
							elif memory_size == 2:
								if increment_pointer:
									LDRH( destination, source, memory_size )
								else:
									LDRH( destination, source )
							elif memory_size == 1:
								if increment_pointer:
									LDRB( destination, source, memory_size )
								else:
									LDRB( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						elif ctype.is_signed_integer():
							if memory_size == 4:
								if increment_pointer:
									LDR( destination, source, memory_size )
								else:
									LDR( destination, source )
							elif memory_size == 2:
								if increment_pointer:
									LDRSH( destination, source, memory_size )
								else:
									LDRSH( destination, source )
							elif memory_size == 1:
								if increment_pointer:
									LDRSB( destination, source, memory_size )
								else:
									LDRSB( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, SRegister):
						if ctype.is_floating_point():
							if memory_size == 4:
								VLDR( destination, source )
								if increment_pointer:
									address_register = Operand(source).get_registers_list()[0]
									ADD( address_register, memory_size )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, DRegister):
						if ctype.is_floating_point():
							if memory_size == 8:
								VLDR( destination, source )
								if increment_pointer:
									address_register = Operand(source).get_registers_list()[0]
									ADD( address_register, memory_size )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					else:
						raise TypeError("Destination must be a general-purpose register")
				else:
					raise TypeError("Source must be a memory operand")
			else:
				raise TypeError("Destination must be a register")
		else:
			raise TypeError("Type must be a C type")

class STORE:
	@staticmethod
	def ELEMENT(destination, source, ctype, increment_pointer = False):
		if isinstance(ctype, peachpy.c.Type):
			if Operand(destination).is_memory_address():
				if Operand(source).is_register():
					memory_size = ctype.get_size(current_function.abi)
					if isinstance(source, GeneralPurposeRegister):
						if ctype.is_integer():
							if memory_size == 4:
								if increment_pointer:
									STR( source, destination, memory_size )
								else:
									STR( source, destination )
							elif memory_size == 2:
								if increment_pointer:
									STRH( source, destination, memory_size )
								else:
									STRH( source, destination )
							elif memory_size == 1:
								if increment_pointer:
									STRB( source, destination, memory_size )
								else:
									STRB( source, destination )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, SRegister):
						if ctype.is_floating_point():
							if memory_size == 4:
								VSTR( source, destination)
								if increment_pointer:
									address_register = Operand(destination).get_registers_list()[0]
									ADD( address_register, memory_size )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, DRegister):
						if ctype.is_floating_point():
							if memory_size == 8:
								VSTR( source, destination )
								if increment_pointer:
									address_register = Operand(destination).get_registers_list()[0]
									ADD( address_register, memory_size )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					else:
						raise TypeError("Source must be a general-purpose register")
				else:
					raise TypeError("Source must be a register")
			else:
				raise TypeError("Destination must be a memory operand")
		else:
			raise TypeError("Type must be a C type")

class ASSUME:
	@staticmethod
	def INITIALIZED(destination):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = AssumeInitializedPseudoInstruction(Operand(destination), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class INIT:
	@staticmethod
	def ONCE(register_class, constant, register = None):
		if register is None:
			origin = inspect.stack() if Function.get_current().collect_origin else None
			register = register_class()
			instruction = LoadConstantPseudoInstruction(Operand(register), Operand(constant), origin = origin)
			if current_stream is not None:
				current_stream.add_instruction(instruction)
			return register
		else:
			return register

class REDUCE:
	@staticmethod
	def SUM(acc, input_type, output_type):
		if all(isinstance(register, AVXRegister) or isinstance(register, SSERegister) for register in acc):
			if isinstance(input_type, peachpy.c.Type) and isinstance(output_type, peachpy.c.Type):
				if input_type.is_floating_point() and output_type.is_floating_point() and input_type.get_size() == output_type.get_size() and input_type.get_size() in [4, 8]:
					is_k10   = Function.get_current().get_target().microarchitecture.get_name() == 'K10' 
					if Target.has_avx():
						SIMD_ADD   = {4: VADDPS, 8: VADDPD}[input_type.get_size()]
						SCALAR_ADD = {4: VADDSS, 8: VADDSD}[input_type.get_size()]
						def SIMD_H2L(destination, source):
							VUNPCKHPD( destination, source, source )
					else:
						SIMD_ADD   = {4: ADDPS, 8: ADDPD}[input_type.get_size()]
						SCALAR_ADD = {4: ADDSS, 8: ADDSD}[input_type.get_size()]
						def SIMD_H2L(destination, source):
							ASSUME.INITIALIZED( destination )
							MOVHLPS( destination, source )
					def SIMD_REDUCE_ADD(acc):
						if is_k10:
							# On K10 HADDPS/HADDPD are efficient 
							if input_type.get_size() == 4:
								HADDPS( acc, acc )
								HADDPS( acc, acc )
							else:
								HADDPD( acc, acc )
						else:
							# On all other CPUs HADDPS/HADDPD are decomposed into two unpack + one add microoperations,
							# but we can do reduction with only one shuffle + one add
							if isinstance(acc, AVXRegister):
								temp = SSERegister()
								VEXTRACTF128( temp, acc, 1 )
								acc = acc.get_oword()
								SIMD_ADD( acc, temp )
							temp = SSERegister()
							SIMD_H2L( temp, acc )
							# Floats need additional reduction step
							if input_type.get_size() == 4:
								SIMD_ADD( acc, temp )
								if Target.has_avx():
									VMOVSHDUP( temp, acc )
								elif Target.has_sse3():
									MOVSHDUP( temp, acc )
								else:
									ASSUME.INITIALIZED( temp )
									UNPCKLPS( acc, acc )
									SIMD_H2L( temp, acc )
							SCALAR_ADD( acc, temp )
						
					for i in range(1, len(acc), 2):
						if isinstance(acc[i - 1], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 1] = acc[i - 1].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_ADD( acc[i - 1], acc[i] )
					for i in range(2, len(acc), 4):
						if isinstance(acc[i - 2], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 2] = acc[i - 2].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_ADD( acc[i - 2], acc[i] )
					for i in range(4, len(acc), 8):
						if isinstance(acc[i - 4], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 4] = acc[i - 4].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_ADD( acc[i - 4], acc[i] )
					for i in range(8, len(acc), 16):
						if isinstance(acc[i - 8], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 8] = acc[i - 8].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_ADD( acc[i - 8], acc[i] )
					SIMD_REDUCE_ADD( acc[0] )
				else:
					raise ValueError("Unsupported combination of input and output types")
			else:
				raise TypeError("Input and output types must be instances of C type")
		else:
			raise TypeError("Unsupported type of accumulator registers")

	@staticmethod
	def MAX(acc, input_type, output_type):
		if all(isinstance(register, AVXRegister) or isinstance(register, SSERegister) for register in acc):
			if isinstance(input_type, peachpy.c.Type) and isinstance(output_type, peachpy.c.Type):
				if input_type.is_floating_point() and output_type.is_floating_point() and input_type.get_size() == output_type.get_size() and input_type.get_size() in [4, 8]:
					if has_avx:
						SIMD_MAX = {4: VMAXPS, 8: VMAXPD}[input_type.get_size()]
						SCALAR_MAX = {4: VMAXSS, 8: VMAXSD}[input_type.get_size()]
						def SIMD_H2L(destination, source):
							VUNPCKHPD( destination, source, source )
					else:
						SIMD_MAX = {4: MAXPS, 8: MAXPD}[input_type.get_size()]
						SCALAR_MAX = {4: MAXSS, 8: MAXSD}[input_type.get_size()]
						def SIMD_H2L(destination, source):
							ASSUME.INITIALIZED( destination )
							MOVHLPS( destination, source )
					def SIMD_REDUCE_MAX(acc):
						if isinstance(acc, AVXRegister):
							temp = SSERegister()
							VEXTRACTF128( temp, acc, 1 )
							acc = acc.get_oword()
							SIMD_MAX( acc, temp )
						temp = SSERegister()
						SIMD_H2L( temp, acc )
						# Floats need additional reduction step
						if input_type.get_size() == 4:
							SIMD_MAX( acc, temp )
							if Target.has_avx():
								VMOVSHDUP( temp, acc )
							elif Target.has_sse3():
								MOVSHDUP( temp, acc )
							else:
								ASSUME.INITIALIZED( temp )
								UNPCKLPS( acc, acc )
								SIMD_H2L( temp, acc )
						SCALAR_MAX( acc, temp )

					for i in range(1, len(acc), 2):
						if isinstance(acc[i - 1], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 1] = acc[i - 1].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MAX( acc[i - 1], acc[i] )
					for i in range(2, len(acc), 4):
						if isinstance(acc[i - 2], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 2] = acc[i - 2].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MAX( acc[i - 2], acc[i] )
					for i in range(4, len(acc), 8):
						if isinstance(acc[i - 4], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 4] = acc[i - 4].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MAX( acc[i - 4], acc[i] )
					for i in range(8, len(acc), 16):
						if isinstance(acc[i - 8], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 8] = acc[i - 8].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MAX( acc[i - 8], acc[i] )
					SIMD_REDUCE_MAX( acc[0] )
				else:
					raise ValueError("Unsupported combination of input and output types")
			else:
				raise TypeError("Input and output types must be instances of C type")
		else:
			raise TypeError("Unsupported type of accumulator registers")

	@staticmethod
	def MIN(acc, input_type, output_type):
		if all(isinstance(register, AVXRegister) or isinstance(register, SSERegister) for register in acc):
			if isinstance(input_type, peachpy.c.Type) and isinstance(output_type, peachpy.c.Type):
				if input_type.is_floating_point() and output_type.is_floating_point() and input_type.get_size() == output_type.get_size() and input_type.get_size() in [4, 8]:
					if Target.has_avx():
						SIMD_MIN = {4: VMINPS, 8: VMINPD}[input_type.get_size()]
						SCALAR_MIN = {4: VMINSS, 8: VMINSD}[input_type.get_size()]
						def SIMD_H2L(destination, source):
							VUNPCKHPD( destination, source, source )
					else:
						SIMD_MIN = {4: MINPS, 8: MINPD}[input_type.get_size()]
						SCALAR_MIN = {4: MINSS, 8: MINSD}[input_type.get_size()]
						def SIMD_H2L(destination, source):
							ASSUME.INITIALIZED( destination )
							MOVHLPS( destination, source )
					def SIMD_REDUCE_MIN(acc):
						if isinstance(acc, AVXRegister):
							temp = SSERegister()
							VEXTRACTF128( temp, acc, 1 )
							acc = acc.get_oword()
							SIMD_MIN( acc, temp )
						temp = SSERegister()
						SIMD_H2L( temp, acc )
						# Floats need additional reduction step
						if input_type.get_size() == 4:
							SIMD_MIN( acc, temp )
							if Target.has_avx():
								VMOVSHDUP( temp, acc )
							elif Target.has_sse3():
								MOVSHDUP( temp, acc )
							else:
								ASSUME.INITIALIZED( temp )
								UNPCKLPS( acc, acc )
								SIMD_H2L( temp, acc )
						SCALAR_MIN( acc, temp )

					for i in range(1, len(acc), 2):
						if isinstance(acc[i - 1], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 1] = acc[i - 1].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MIN( acc[i - 1], acc[i] )
					for i in range(2, len(acc), 4):
						if isinstance(acc[i - 2], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 2] = acc[i - 2].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MIN( acc[i - 2], acc[i] )
					for i in range(4, len(acc), 8):
						if isinstance(acc[i - 4], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 4] = acc[i - 4].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MIN( acc[i - 4], acc[i] )
					for i in range(8, len(acc), 16):
						if isinstance(acc[i - 8], AVXRegister) or isinstance(acc[i], AVXRegister):
							acc[i - 8] = acc[i - 8].get_hword()
							acc[i] = acc[i].get_hword()
						SIMD_MIN( acc[i - 8], acc[i] )
					SIMD_REDUCE_MIN( acc[0] )
				else:
					raise ValueError("Unsupported combination of input and output types")
			else:
				raise TypeError("Input and output types must be instances of C type")
		else:
			raise TypeError("Unsupported type of accumulator registers")

class SWAP:
	@staticmethod
	def REGISTERS(register_x, register_y):
		if isinstance(register_x, Register) and isinstance(register_y, Register):
			if register_x.type == register_y.type and register_x.size == register_y.size:
				register_x.number, register_y.number = register_y.number, register_x.number
			else:
				raise ValueError("Registers {0} and {1} have incompatible register types".format(register_x, register_y))
		else:
			raise TypeError("Arguments must be of register type")

def ADD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADDSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADCSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ADCSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SUBSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBCSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('SBCSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSBSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSBSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RSCSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('RSCSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AND(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('AND', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ANDSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BIC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BIC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BICSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('BICSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORR(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORREQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORREQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORRSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('ORRSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EOR(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EOR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EOREQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EOREQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSEQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSEQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSNE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSNE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSCS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSCS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSHS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSHS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSCC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSCC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSLO(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSLO', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSMI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSMI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSPL(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSPL', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSVS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSVS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSVC(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSVC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSHI(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSLS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSLS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSGE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSGE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSLT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSLT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSGT(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSGT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def EORSLE(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = ArithmeticInstruction('EORSLE', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMP(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMP', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPEQ(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPEQ', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPNE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPCS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPCS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPHS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPHS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPCC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPCC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLO(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPLO', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPMI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPMI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPPL(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPPL', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPVS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPVS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPVC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPVC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPHI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPHI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPLS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPGE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPGE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPLT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPGT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPGT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMPLE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMN(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMN', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNEQ(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNEQ', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNNE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNNE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNCS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNCS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNHS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNHS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNCC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNCC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNLO(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNLO', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNMI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNMI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNPL(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNPL', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNVS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNVS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNVC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNVC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNHI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNHI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNLS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNLS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNGE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNGE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNLT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNLT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNGT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNGT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMNLE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('CMNLE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TST(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TST', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTEQ(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTEQ', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTNE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTNE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTCS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTCS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTHS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTHS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTCC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTCC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTLO(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTLO', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTMI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTMI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTPL(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTPL', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTVS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTVS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTVC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTVC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTHI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTHI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTLS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTLS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTGE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTGE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTLT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTLT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTGT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTGT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TSTLE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TSTLE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQ(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQ', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQEQ(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQEQ', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQNE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQNE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQCS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQCS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQHS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQHS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQCC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQCC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQLO(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQLO', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQMI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQMI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQPL(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQPL', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQVS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQVS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQVC(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQVC', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQHI(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQHI', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQLS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQLS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQGE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQGE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQLT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQLT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQGT(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQGT', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEQLE(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CompareInstruction('TEQLE', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOV(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOV', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVEQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVEQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVNE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVNE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVCS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVCS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVHS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVHS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVCC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVCC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLO(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVLO', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVMI(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVMI', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVPL(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVPL', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVVS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVVS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVVC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVVC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVHI(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVHI', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVLS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVGE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVGE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLT(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVLT', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVGT(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVGT', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVLE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction('MOVS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUSH(register_list):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PushPopInstruction('PUSH', Operand(register_list), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def POP(register_list):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PushPopInstruction('POP', Operand(register_list), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LDR(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('LDR', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def STR(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('STR', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LDRH(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('LDRH', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LDRSH(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('LDRSH', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def STRH(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('STRH', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LDRB(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('LDRB', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LDRSB(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('LDRSB', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def STRB(register, address, increment = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadStoreInstruction('STRB', Operand(register), Operand(address), Operand(increment), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def B(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('B', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BEQ(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BEQ', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BNE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BNE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BCS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BCS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BHS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BHS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BCC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BCC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BLO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BMI(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BMI', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BPL(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BPL', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BVS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BVS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BVC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BVC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BHI(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BHI', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BLS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BGE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BGE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLT(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BLT', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BGT(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BGT', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BranchInstruction('BLE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

class VADD:
	@staticmethod
	def I8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VADD.I8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VADD.I16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VADD.I32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VADD.I64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPNeonBinaryArithmeticInstruction('VADD.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionBinaryArithmeticInstruction('VADD.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VADDL:
	@staticmethod
	def S8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VADDL.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VADDL.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VADDL.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VADDL.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VADDL.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VADDL.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VSUB:
	@staticmethod
	def I8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VSUB.I8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VSUB.I16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VSUB.I32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VSUB.I64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPNeonBinaryArithmeticInstruction('VSUB.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionBinaryArithmeticInstruction('VSUB.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VSUBL:
	@staticmethod
	def S8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VSUBL.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VSUBL.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VSUBL.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VSUBL.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VSUBL.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VSUBL.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VMUL:
	@staticmethod
	def I8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMUL.I8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMUL.I16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMUL.I32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPNeonBinaryArithmeticInstruction('VMUL.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionBinaryArithmeticInstruction('VMUL.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VMULL:
	@staticmethod
	def S8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def P8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonWideArithmeticInstruction('VMULL.P8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VMIN:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMIN.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VMAX:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VMAX.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VABD:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VABD.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VACGE:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VACGE.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VACGT:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VACGT.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VACLE:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VACLE.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VACLT:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VACLT.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VAND(object):
	@staticmethod
	def __new__(cls, destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VAND', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VBIC(object):
	@staticmethod
	def __new__(cls, destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VBIC', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VORR(object):
	@staticmethod
	def __new__(cls, destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VORR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VORN(object):
	@staticmethod
	def __new__(cls, destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VORN', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

def VEOR(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		(destination, source_x, source_y) = (destination, destination, source_x)
	instruction = NeonArithmeticInstruction('VEOR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

class VPADD:
	@staticmethod
	def I8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPADD.I8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPADD.I16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPADD.I32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPADD.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VPMIN:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMIN.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VPMAX:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VPMAX.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VQADD:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.S64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQADD.U64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VQSUB:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.S64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VQSUB.U64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VHADD:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHADD.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHADD.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHADD.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHADD.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHADD.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHADD.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VHSUB:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHSUB.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHSUB.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHSUB.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHSUB.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHSUB.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VHSUB.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VRHADD:
	@staticmethod
	def S8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRHADD.S8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRHADD.S16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def S32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRHADD.S32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U8(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRHADD.U8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U16(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRHADD.U16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def U32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRHADD.U32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VRECPS:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRECPS.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VRSQRTS:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = NeonArithmeticInstruction('VRSQRTS.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VTST:
	@staticmethod
	def I8(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonArithmeticInstruction('VTST.8', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonArithmeticInstruction('VTST.16', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(destination, source_x, source_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonArithmeticInstruction('VTST.32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VNMUL:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPSinglePrecisionMultiplyAddInstruction('VNMUL.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionBinaryArithmeticInstruction('VNMUL.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VDIV:
	@staticmethod
	def F32(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPSinglePrecisionMultiplyAddInstruction('VDIV.F32', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionBinaryArithmeticInstruction('VDIV.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VSQRT:
	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionUnaryArithmeticInstruction('VSQRT.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VABS:
	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionUnaryArithmeticInstruction('VABS.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VNEG:
	@staticmethod
	def F64(destination, source_x, source_y = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		if source_y is None:
			(destination, source_x, source_y) = (destination, destination, source_x)
		instruction = VFPDoublePrecisionUnaryArithmeticInstruction('VNEG.F64', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VMLA:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPNeonMultiplyAddInstruction('VMLA.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VMLA.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VMLS:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPNeonMultiplyAddInstruction('VMLS.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VMLS.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VNMLA:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPSinglePrecisionMultiplyAddInstruction('VNMLA.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VNMLA.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VNMLS:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPSinglePrecisionMultiplyAddInstruction('VNMLS.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VNMLS.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VFMA:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPNeonMultiplyAddInstruction('VFMA.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VFMA.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VFMS:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPNeonMultiplyAddInstruction('VFMS.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VFMS.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VFNMA:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPSinglePrecisionMultiplyAddInstruction('VFNMA.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VFNMA.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

class VFNMS:
	@staticmethod
	def F32(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPSinglePrecisionMultiplyAddInstruction('VFNMS.F32', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(accumulator, factor_x, factor_y):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VFPDoublePrecisionMultiplyAddInstruction('VFNMS.F64', Operand(accumulator), Operand(factor_x), Operand(factor_y), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

def VLDR(register, address):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreInstruction("VLDR", Operand(register), Operand(address), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSTR(register, address):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreInstruction("VSTR", Operand(register), Operand(address), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VLDM(source, destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreMultipleInstruction("VLDM", Operand(source), Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VLDMIA(source, destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreMultipleInstruction("VLDMIA", Operand(source), Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VLDMDB(source, destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreMultipleInstruction("VLDMDB", Operand(source), Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSTM(source, destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreMultipleInstruction("VSTM", Operand(source), Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSTMIA(source, destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreMultipleInstruction("VSTMIA", Operand(source), Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSTMDB(source, destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPLoadStoreMultipleInstruction("VSTMDB", Operand(source), Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUSH(register_list):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPPushPopInstruction("VPUSH", Operand(register_list), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
	
def VPOP(register_list):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = VFPPushPopInstruction("VPOP", Operand(register_list), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

class VLD1:
	@staticmethod
	def I8(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VLD1.8", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VLD1.16", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VLD1.32", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I64(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VLD1.64", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VLD1.32", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction
		
class VST1:
	@staticmethod
	def I8(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VST1.8", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I16(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VST1.16", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I32(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VST1.32", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def I64(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VST1.64", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(address, register_list, increment = None):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = NeonLoadStoreInstruction("VST1.32", Operand(address), Operand(register_list), Operand(increment), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction
		
class VMOV(object):
	@staticmethod
	def __new__(cls, destination, source):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VfpNeonMovInstruction('VMOV', Operand(destination), Operand(source), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F32(destination, source):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VfpNeonMovInstruction('VMOV.F32', Operand(destination), Operand(source), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def F64(destination, source):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = VfpNeonMovInstruction('VMOV.F64', Operand(destination), Operand(source), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction
