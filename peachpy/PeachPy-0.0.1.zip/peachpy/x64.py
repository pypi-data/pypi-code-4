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
supported_isa_extensions = ['CMOV', 'MMX', 'MMX+', '3dnow!', '3dnow!+', '3dnow! Prefetch',
							'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2',
							'AVX', 'AVX2', 'FMA3', 'FMA4', 'F16C', 'XOP',
							'MOVBE', 'POPCNT', 'LZCNT', 'BMI', 'BMI2', 'TBM', 'ADX',
							'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ']

class Parameter(peachpy.c.Parameter):
	def __init__(self, parameter):
		if isinstance(parameter, peachpy.c.Parameter):
			super(Parameter, self).__init__(parameter.name, parameter.type)
			self.register = None
			self.stack_offset = None
		else:
			raise TypeError("Invalid parameter type {0}".format(type(parameter)))

class Microarchitecture(object):
	supported_microarchitectures = ['Unknown',
	                                'Prescott',
	                                'Conroe', 'Penryn', 'Nehalem', 'SandyBridge', 'IvyBridge', 'Haswell', 
	                                'Bonnell', 'Saltwell', 'Silvermont',
	                                'K8', 'K10', 'Bulldozer', 'Piledriver', 'Steamroller',
	                                'Bobcat', 'Jaguar']

	supported_isa_extensions = {'Unknown'     : set(['CMOV', 'MMX', 'MMX+', '3dnow!', '3dnow!+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2', 'POPCNT', 'LZCNT', 'MOVBE', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'AVX', 'AVX2', 'XOP', 'FMA4', 'FMA3', 'F16C', 'BMI', 'BMI2', 'TBM', 'ADX']),
	                            'Prescott'    : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3']),
	                            'Conroe'      : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3']),
	                            'Penryn'      : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1']),
	                            'Nehalem'     : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AES', 'PCLMULQDQ', 'POPCNT']),
	                            'SandyBridge' : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'POPCNT', 'AVX']),
	                            'IvyBridge'   : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'POPCNT', 'AVX', 'F16C', 'RDRAND']),
	                            'Haswell'     : set(['CMOV', 'MMX', 'MMX+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'POPCNT', 'LZCNT', 'MOVBE', 'AVX', 'F16C', 'AVX2', 'FMA3', 'BMI', 'BMI2', 'RDRAND']),
	                            'Bonnell'     : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE']),
	                            'Saltwell'    : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE']),
	                            'Silvermont'  : set(['CMOV', 'MMX', 'MMX+', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AES', 'PCLMULQDQ', 'RDRAND', 'POPCNT', 'MOVBE']),
	                            'K8'          : set(['CMOV', 'MMX', 'MMX+', '3dnow!', '3dnow!+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3']),
	                            'K10'         : set(['CMOV', 'MMX', 'MMX+', '3dnow!', '3dnow!+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSE4A', 'POPCNT', 'LZCNT']),
	                            'Bulldozer'   : set(['CMOV', 'MMX', 'MMX+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2', 'POPCNT', 'LZCNT', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'AVX', 'XOP', 'FMA4']),
	                            'Piledriver'  : set(['CMOV', 'MMX', 'MMX+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2', 'POPCNT', 'LZCNT', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'AVX', 'XOP', 'FMA4', 'FMA3', 'F16C', 'BMI', 'TBM']),
	                            'Steamroller' : set(['CMOV', 'MMX', 'MMX+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2', 'POPCNT', 'LZCNT', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'AVX', 'XOP', 'FMA4', 'FMA3', 'F16C', 'BMI', 'TBM']),
	                            'Bobcat'      : set(['CMOV', 'MMX', 'MMX+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A']),
	                            'Jaguar'      : set(['CMOV', 'MMX', 'MMX+', '3dnow! Prefetch', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4A', 'SSE4.1', 'SSE4.2', 'POPCNT', 'LZCNT', 'AES', 'VAES', 'PCLMULQDQ', 'VPCLMULQDQ', 'MOVBE', 'AVX', 'F16C', 'BMI']) }

	def __init__(self, name):
		super(Microarchitecture, self).__init__()
		if name in Microarchitecture.supported_microarchitectures:
			self.name = name
			self.supported_isa_extensions = Microarchitecture.supported_isa_extensions[self.name]
		else:
			raise ValueError('Unsupported microarchitecture {0}: only ({1}) microarchitectures are supported on this architecture'.format(name, ', '.join(Microarchitecture.supported_microarchitectures)))

	def __str__(self):
		descriptions = {'Unknown': 'Default',
		                'Prescott': 'Intel Prescott',
		                'Conroe': 'Intel Conroe',
		                'Penryn': 'Intel Penryn',
		                'Nehalem': 'Intel Nehalem',
		                'SandyBridge': 'Intel Sandy Bridge',
		                'IvyBridge': 'Intel Ivy Bridge',
		                'Haswell': 'Intel Haswell', 
		                'Bonnell': 'Intel Bonnell',
		                'Saltwell': 'Intel Saltwell',
		                'Silvermont': 'Intel Silvermont',
		                'K8': 'AMD K8',
		                'K10': 'AMD K10',
		                'Bulldozer': 'AMD Bulldozer',
		                'Piledriver': 'AMD Piledriver',
		                'Steamroller': 'AMD Steamroller',
		                'Bobcat': 'AMD Bobcat',
		                'Jaguar': 'AMD Jaguar'}
		return descriptions[self.get_name()]

	def get_name(self):
		return self.name

	def get_number(self):
		return Microarchitecture.supported_microarchitectures.index(self.get_name())

	def get_int_eu_width(self):
		return {'Unknown': 128,
		        'Prescott': 64,
		        'Conroe': 128,
		        'Penryn': 128,
		        'Nehalem': 128,
		        'SandyBridge': 128,
		        'IvyBridge': 128,
		        'Haswell': 256, 
		        'Bonnell': 128,
		        'Saltwell': 128,
		        'Silvermont': 128,
		        'K8': 64,
		        'K10': 128,
		        'Bulldozer': 128,
		        'Piledriver': 128,
		        'Steamroller': 256,
		        'Bobcat': 64,
		        'Jaguar': 128}[self.name]

	def get_fp_eu_width(self):
		return {'Unknown': 128,
		        'Prescott': 64,
		        'Conroe': 128,
		        'Penryn': 128,
		        'Nehalem': 128,
		        'SandyBridge': 256,
		        'IvyBridge': 256,
		        'Haswell': 256, 
		        'Bonnell': 64,
		        'Saltwell': 64,
		        'Silvermont': 128,
		        'K8': 64,
		        'K10': 128,
		        'Bulldozer': 128,
		        'Piledriver': 128,
		        'Steamroller': 256,
		        'Bobcat': 64,
		        'Jaguar': 128}[self.name]

	def get_ld_eu_width(self):
		return {'Unknown': 128,
		        'Prescott': 64,
		        'Conroe': 128,
		        'Penryn': 128,
		        'Nehalem': 128,
		        'SandyBridge': 256,
		        'IvyBridge': 256,
		        'Haswell': 256, 
		        'Bonnell': 128,
		        'Saltwell': 128,
		        'Silvermont': 128,
		        'K8': 64,
		        'K10': 128,
		        'Bulldozer': 128,
		        'Piledriver': 128,
		        'Steamroller': 256,
		        'Bobcat': 64,
		        'Jaguar': 128}[self.name]

	def get_st_eu_width(self):
		return {'Unknown': 128,
		        'Prescott': 64,
		        'Conroe': 128,
		        'Penryn': 128,
		        'Nehalem': 128,
		        'SandyBridge': 128,
		        'IvyBridge': 128,
		        'Haswell': 256, 
		        'Bonnell': 128,
		        'Saltwell': 128,
		        'Silvermont': 128,
		        'K8': 64,
		        'K10': 64,
		        'Bulldozer': 128,
		        'Piledriver': 128,
		        'Steamroller': 256,
		        'Bobcat': 64,
		        'Jaguar': 128}[self.name]

class Target:
	dependent_isa_extensions = {
	     'MMX': ['MMX+', '3dnow!'],
	     '3dnow!': ['3dnow!+'],
	     'SSE': ['SSE2'],
	     'SSE2': ['SSE3', 'AES', 'PCLMULQDQ'],
	     'SSE3': ['SSSE3', 'SSE4A'],
	     'SSSE3': ['SSE4.1'],
	     'SSE4.1': ['SSE4.2'],
	     'AES': ['VAES'],
	     'PCLMULQDQ': ['VPCLMULQDQ'],
	     'AVX': ['AVX2', 'FMA3', 'FMA4', 'XOP', 'F16C', 'VAES', 'VPCLMULQDQ'],
	     'BMI': ['BMI2']
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
	def get_int_eu_width():
		return Function.get_current().get_target().microarchitecture.get_int_eu_width()

	@staticmethod
	def get_fp_eu_width():
		return Function.get_current().get_target().microarchitecture.get_fp_eu_width()

	@staticmethod
	def get_ld_eu_width():
		return Function.get_current().get_target().microarchitecture.get_ld_eu_width()

	@staticmethod
	def get_st_eu_width():
		return Function.get_current().get_target().microarchitecture.get_st_eu_width()

	@staticmethod
	def has_cmov():
		return 'CMOV' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_mmx():
		return 'MMX' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_mmx_plus():
		return 'MMX+' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_3dnow():
		return '3dnow!' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_3dnow_plus():
		return '3dnow!+' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_3dnow_prefetch():
		return '3dnow! Prefetch' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_sse():
		return 'SSE' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_sse2():
		return 'SSE2' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_sse3():
		return 'SSE3' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_ssse3():
		return 'SSSE3' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_sse4a():
		return 'SSE4A' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_sse4_1():
		return 'SSE4.1' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_sse4_2():
		return 'SSE4.2' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_popcnt():
		return 'POPCNT' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_lzcnt():
		return 'LZCNT' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_movbe():
		return 'MOVBE' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_aes():
		return 'AES' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vaes():
		return 'VAES' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_pclmulqdq():
		return 'PCLMULQDQ' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_vpclmulqdq():
		return 'VPCLMULQDQ' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_avx():
		return 'AVX' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_avx2():
		return 'AVX2' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_xop():
		return 'XOP' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_fma4():
		return 'FMA4' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_fma3():
		return 'FMA3' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_fma():
		return Target.has_fma3() or Target.has_fma4()

	@staticmethod
	def has_f16c():
		return 'F16C' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_bmi():
		return 'BMI' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_bmi2():
		return 'BMI2' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_tbm():
		return 'TBM' in Function.get_current().get_target().isa_extensions

	@staticmethod
	def has_adx():
		return 'ADX' in Function.get_current().get_target().isa_extensions

class Assembler(peachpy.codegen.CodeGenerator):
	def __init__(self, abi):
		super(Assembler, self).__init__()
		if isinstance(abi, peachpy.c.ABI):
			if abi.get_name() in ["x64-ms", "x64-sysv", "x32"]:
				self.abi = abi
			else:
				raise ValueError('Unsupported abi {0}: only "x64-ms", "x64-sysv" and "x32" ABIs are supported on this architecture'.format(abi))
		else:
			raise TypeError('Wrong type of ABI object')
		self.functions = list()

	def __str__(self):
		return self.get_code()

	def find_functions(self, name):
		return [function for function in self.functions if function.name == name]

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
		self.arguments = [peachpy.x64.Parameter(argument) for argument in arguments]
		self.target = Target(microarchitecture, exclude_isa_extensions)
		self.collect_origin = collect_origin
		self.dump_intermediate_assembly = dump_intermediate_assembly
		self.check_only = check_only
		self.report_generation = report_generation
		self.report_live_registers = report_live_registers
		self.ticks = None
		self.assembly_cache = assembly_cache
		
		# Determine parameters locations 
		if assembler.abi.name == 'x64-ms':
			floating_point_parameter_registers = (xmm0, xmm1, xmm2, xmm3)
			integer_parameter_registers = (rcx, rdx, r8, r9)
			for (index, argument) in enumerate(self.arguments):
				if index < 4:
					if argument.get_type().is_floating_point():
						argument.register = floating_point_parameter_registers[index]
					else:
						argument.register = integer_parameter_registers[index]
				else:
					argument.stack_offset = (index + 1) * 8
		elif assembler.abi.name == 'x64-sysv':
			available_floating_point_registers = [xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7]
			available_integer_registers = [rdi, rsi, rdx, rcx, r8, r9]
			stack_offset = 8
			for argument in self.arguments:
				if argument.get_type().is_floating_point() and len(available_floating_point_registers) > 0:
					argument.register = available_floating_point_registers.pop(0)
				elif not argument.get_type().is_floating_point() and len(available_integer_registers) > 0: 
					argument.register = available_integer_registers.pop(0)
				else:
					argument.stack_offset = stack_offset
					stack_offset += 8
		else:
			raise ValueError("Unsupported assembler ABI") 

		self.symbol_name = "_" + name + "_" + microarchitecture
		self.abi = self.assembler.abi
		self.instructions = list()
		self.constants = list()
		self.stack_frame = StackFrame(self.abi)
		self.local_variables_count = 0
		self.virtual_registers_count = 0x40
		self.uses_avx = False
		self.uses_mmx = False
		self.conflicting_registers = dict()
		self.possible_register_allocations = dict()
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
				function_label = self.abi.function_prefix + self.symbol_name
				constants_label = self.symbol_name + "_constants"
				if len(self.constants) > 0:
					if self.abi.name == 'x64-ms':
						self.assembler.add_line('section .rdata${0} rdata align={1}'.format(string.ascii_lowercase[self.get_target().microarchitecture.get_number()], 32))
					else:
						self.assembler.add_line('%ifidn __OUTPUT_FORMAT__, elf64')
						self.assembler.add_line('section .rodata.{0} progbits alloc noexec nowrite align={1}'.format(self.get_target().microarchitecture.get_name(), 32))
						self.assembler.add_line('%else')
						self.assembler.add_line('section .rodata align={0}'.format(32))
						self.assembler.add_line('%endif')
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
		
				if self.abi.name == 'x64-ms':
					self.assembler.add_line('section .text${0} code align=16'.format(string.ascii_lowercase[self.get_target().microarchitecture.get_number()]))
					self.assembler.add_line("global " + function_label)
					self.assembler.add_line(function_label + ':')
				else:
					self.assembler.add_line('%ifidn __OUTPUT_FORMAT__, elf64')
					self.assembler.add_line('section .text.{0} progbits alloc exec nowrite align=16'.format(self.get_target().microarchitecture.get_name()))
					self.assembler.add_line("global " + function_label)
					self.assembler.add_line(function_label + ':')
					self.assembler.add_line('%else')
					self.assembler.add_line('section .text')
					self.assembler.add_line("global _" + function_label)
					self.assembler.add_line('_' + function_label + ':')
					self.assembler.add_line('%endif')
				self.assembler.indent()
				for instruction in self.instructions:
					if isinstance(instruction, Instruction):
						constant = instruction.get_constant()
						if constant is not None:
							constant.prefix = constants_label
						if self.report_live_registers:
							xmm_live_registers = sum(isinstance(register, SSERegister) or isinstance(register, AVXRegister) for register in instruction.live_registers)
							mm_live_registers = sum(isinstance(register, MMXRegister) for register in instruction.live_registers)
							gp_live_registers = sum(isinstance(register, GeneralPurposeRegister) for register in instruction.live_registers)
							self.assembler.add_line("{0:70s} ; xmm: {1:2}\tmm: {2:2}\tgp: {3:2}".format(instruction, xmm_live_registers, mm_live_registers, gp_live_registers))
						else:
							self.assembler.add_line(str(instruction))
					elif isinstance(instruction, Label):
						self.assembler.add_line(str(instruction), indent = 0)
					else:
						self.assembler.add_line(str(instruction))
				self.assembler.dedent()
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
			if instruction.is_avx():
				self.uses_avx = True
			if instruction.is_mmx():
				self.uses_mmx = True
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
			elif isinstance(instruction, CompareAndBranchInstruction):
				new_instructions.append(instruction.compare)
				new_instructions.append(instruction.branch)
			else:
				new_instructions.append(instruction)
		self.instructions = new_instructions
		
	def generate_prolog_and_epilog(self):
		prologue_instructions = self.stack_frame.generate_prologue(self.uses_avx, self.reserve_rbp)
		epilogue_instructions = self.stack_frame.generate_epilogue(self.uses_mmx, self.uses_avx, self.reserve_rbp)
		new_instructions = list()
		for instruction in self.instructions:
			if isinstance(instruction, LabelMark):
				new_instructions.append(instruction)
				if instruction.name == 'ENTRY':
					new_instructions.extend(prologue_instructions)
			elif isinstance(instruction, RetInstruction):
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
			if isinstance(instruction, RetInstruction) or isinstance(instruction, ReturnInstruction):
				ret_instructions.append(index)
		return ret_instructions

	def determine_branches(self):
		label_table = self.get_label_table()
		for instruction in self.instructions:
			if isinstance(instruction, LabelMark):
				instruction.input_branches = set()

		for i, instruction in enumerate(self.instructions):
			if isinstance(instruction, ConditionalJumpInstruction) or isinstance(instruction, JmpInstruction):
				target_label = instruction.destination
				target_index = label_table[target_label]
				self.instructions[target_index].input_branches.add(i)

	def reserve_registers(self):
		# If the stack needs to be realigned (there are AVX variables which need 32-byte alignment)
		# and there are on-stack variables which are addressed using stack pointer, then
		# we preserve the old stack pointer in the RBP register
		self.reserve_rbp = bool(filter(bool, [argument.stack_offset for argument in self.arguments])) and bool(self.stack_frame.avx_variables)

		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				for register in instruction.get_input_registers_list():
					if isinstance(register, GeneralPurposeRegister) and register.get_qword() == rbp:
						raise ValueError('Instruction {0} reads the reserved register RBP'.format(instruction))
				for register in instruction.get_output_registers_list():
					if isinstance(register, GeneralPurposeRegister) and register.get_qword() == rbp:
						raise ValueError('Instruction {0} modifies the reserved register RBP'.format(instruction))

	def determine_available_registers(self):
		processed_branches = set()
		label_table = self.get_label_table()

		def mark_available_registers(instructions, start, initial_available_registers):
			available_registers = set(initial_available_registers)
			for i in range(start, len(instructions)):
				instruction = instructions[i]
				if isinstance(instruction, Instruction):
					instruction.available_registers = set(available_registers)
					if isinstance(instruction, ConditionalJumpInstruction) or isinstance(instruction, JmpInstruction):
						if i not in processed_branches:
							target_label = instruction.destination
							target_index = label_table[target_label]
							processed_branches.add(i)
							mark_available_registers(instructions, target_index, available_registers)
						if isinstance(instruction, JmpInstruction):
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
			if hasattr(instruction, 'is_visited'):
				instruction.is_visited = False

		def mark_live_registers(instructions, exit_point, initial_live_registers):
			live_registers = dict(initial_live_registers)
			# Walk from the bottom to top of the linear block
			for i in range(exit_point, -1, -1):
				instruction = instructions[i]
				if isinstance(instruction, JmpInstruction) and i != exit_point:
					return
				elif isinstance(instruction, Instruction):
					# First mark registers which are written to by this instruction as non-live
					# Then mark registers which are read by this instruction as live
					for output_register in instruction.get_output_registers_list():
						# Instructions which write to 32-bit register implicitly zero out its upper 32 bit
						if isinstance(output_register, GeneralPurposeRegister32):
							output_register = output_register.get_qword()
						# Instructions which write to xmm register implicitly zero out the upper part of the corresponding ymm register
						if isinstance(output_register, SSERegister) and instruction.is_avx():
							output_register = output_register.get_hword()
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

					instruction.live_registers = set([Register.from_parts(id, mask) for (id, mask) in live_registers.iteritems()])
				elif isinstance(instruction, LabelMark):
					for entry_point in instruction.input_branches:
						if not instructions[entry_point].is_visited:
							instructions[entry_point].is_visited = True
							mark_live_registers(instructions, entry_point, live_registers)

		exit_points = self.find_exit_points()
		for exit_point in exit_points:
			mark_live_registers(self.instructions, exit_point, set())

	def check_live_registers(self):
		all_registers = self.abi.volatile_registers + list(reversed(self.abi.argument_registers)) + self.abi.callee_save_registers
		if self.reserve_rbp:
			all_registers.remove(rbp)
		available_registers = { Register.GPType: list(), Register.MMXType: list(), Register.AVXType: list() }
		for register in all_registers:
			if register not in available_registers[register.type]:
				available_registers[register.type].append(register)
		for instruction in self.instructions:
			live_registers = { Register.GPType: set(), Register.MMXType: set(), Register.AVXType: set() }
			if isinstance(instruction, Instruction):
				for live_register in instruction.live_registers:
					live_registers[live_register.type].add(live_register)
				for register_type in live_registers.iterkeys():
					if len(live_registers[register_type]) > len(available_registers[register_type]):
						if instruction.source_code:
							raise RegisterAllocationError("Not enough available registers to allocate live registers at instruction {0}, line {1}, file {2}".format(instruction.source_code, instruction.line_number, instruction.source_file))
						else:
							raise RegisterAllocationError("Not enough available registers to allocate live registers at instruction {0}".format(instruction))

	def determine_register_relations(self):
		all_registers = self.abi.volatile_registers + list(reversed(self.abi.argument_registers)) + self.abi.callee_save_registers
		if self.reserve_rbp:
			all_registers.remove(rbp)
		available_registers = { Register.GPType: list(), Register.MMXType: list(), Register.AVXType: list() }
		for register in all_registers:
			if register not in available_registers[register.type]:
				available_registers[register.type].append(register)
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				virtual_live_registers = [register for register in instruction.live_registers if register.is_virtual()]
				for registerX in virtual_live_registers:
					if registerX.get_id() not in self.possible_register_allocations:
						self.possible_register_allocations[registerX.get_id()] = [register.get_id() for register in available_registers[registerX.type]]
						self.unallocated_registers.append(registerX.get_id())
					if registerX.get_id() not in self.conflicting_registers:
						self.conflicting_registers[registerX.get_id()] = set()
					for registerY in virtual_live_registers:
						if registerX.get_id() != registerY.get_id() and registerX.type == registerY.type:
							self.conflicting_registers[registerX.get_id()].add(registerY.get_id())
		# Mark available physical registers for each virtual register
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				virtual_live_register_ids = [register.get_id() for register in instruction.live_registers if register.is_virtual()]
				physical_live_register_ids = [register.get_id() for register in instruction.live_registers if not register.is_virtual()]
				for virtual_register_id in virtual_live_register_ids:
					for physical_register_id in physical_live_register_ids:
						if physical_register_id in self.possible_register_allocations[virtual_register_id]:
							self.possible_register_allocations[virtual_register_id].remove(physical_register_id)

	# Updates information about registers to be saved/restored in the function prologue/epilogue
	def update_stack_frame(self):
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				self.stack_frame.preserve_registers(instruction.get_output_registers_list())

	def allocate_registers(self):
		register_allocation = dict()
		for register in self.possible_register_allocations.iterkeys():
			register_allocation[register] = None

		def bind_register(virtual_register_id, physical_register_id):
			# Remove option to allocate any conflicting virtual register to the same physical register
			for conflicting_register_id in self.conflicting_registers[virtual_register_id]:
				if physical_register_id in self.possible_register_allocations[conflicting_register_id]:
					self.possible_register_allocations[conflicting_register_id].remove(physical_register_id)
			register_allocation[virtual_register_id] = physical_register_id

		def is_allocated(virtual_register_id):
			return bool(register_allocation[virtual_register_id])

		# First allocate parameters
		for instruction in self.instructions:
			if isinstance(instruction, LoadParameterPseudoInstruction):
				if instruction.parameter.register:
					if instruction.destination.register.is_virtual():
						if not is_allocated(instruction.destination.register.get_id()):
							if instruction.parameter.register.get_id() in self.possible_register_allocations[instruction.destination.register.get_id()]:
								bind_register(instruction.destination.register.get_id(), instruction.parameter.register.get_id())
		# Now allocate all other registers
		while self.unallocated_registers:
			virtual_register_id = self.unallocated_registers.pop(0)
			if not is_allocated(virtual_register_id):
				assert self.possible_register_allocations[virtual_register_id]
				physical_register_id = self.possible_register_allocations[virtual_register_id][0]
				bind_register(virtual_register_id, physical_register_id)
		for instruction in self.instructions:
			if isinstance(instruction, Instruction):
				for input_register in instruction.get_input_registers_list():
					if input_register.is_virtual():
						input_register.bind(register_allocation[input_register.get_id()])
				for output_register in instruction.get_output_registers_list():
					if output_register.is_virtual():
						if output_register.get_id() in register_allocation:
							output_register.bind(register_allocation[output_register.get_id()])

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
					type = instruction.parameter.get_type()
					if type.is_pointer() or type.is_size() or type.get_primitive_type().get_size() * 8 == parameter.register.size:
						# If parameter is in a register, use register-register move:
						if instruction.destination.register != parameter.register:
							new_instruction = MOV( instruction.destination.register, parameter.register )
							new_instruction.live_registers = instruction.live_registers
							new_instruction.available_registers = instruction.available_registers
							new_instructions.append(new_instruction)
					elif type.get_primitive_type().get_size() * 8 > parameter.register.size:
						if type.get_primitive_type().is_signed_integer():
							if type.get_primitive_type().get_size() == 1:
								new_instruction = MOVSX( instruction.destination.register, parameter.register.get_low_byte() )
							elif type.get_primitive_type().get_size() == 2:
								new_instruction = MOVSX( instruction.destination.register, parameter.register.get_word() )
							elif type.get_primitive_type().get_size() == 4:
								new_instruction = MOVSX( instruction.destination.register, parameter.register.get_dword() )
							new_instruction.live_registers = instruction.live_registers
							new_instruction.available_registers = instruction.available_registers
							new_instructions.append(new_instruction)
						else:
							if type.get_primitive_type().get_size() == 1:
								if isinstance(instruction.destination.register, GeneralPurposeRegister64):
									new_instruction = MOVZX( instruction.destination.register.get_dword(), parameter.register.get_low_byte() )
								else:
									new_instruction = MOVZX( instruction.destination.register, parameter.register.get_low_byte() )
							elif type.get_primitive_type().get_size() == 2:
								if isinstance(instruction.destination.register, GeneralPurposeRegister64):
									new_instruction = MOVZX( instruction.destination.register.get_dword(), parameter.register.get_word() )
								else:
									new_instruction = MOVZX( instruction.destination.register, parameter.register.get_word() )
							elif type.get_primitive_type().get_size() == 4:
								if isinstance(instruction.destination.register, GeneralPurposeRegister64):
									new_instruction = MOV( instruction.destination.register.get_dword(), parameter.register.get_dword() )
								else:
									new_instruction = MOVZX( instruction.destination.register, parameter.register.get_dword() )
							new_instruction.live_registers = instruction.live_registers
							new_instruction.available_registers = instruction.available_registers
							new_instructions.append(new_instruction)
					else:
						raise TypeError('Can not load element of type {0} into register {1}'.format(type, parameter.register))
				else:
 					parameter_address = self.stack_frame.get_parameters_address(self.reserve_rbp) + parameter.stack_offset
					new_instruction = MOV( instruction.destination.register, [parameter_address] )
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
				# 32-bit moves zero the upper part which can be purposely used
				if instruction.destination != instruction.source or instruction.destination.is_general_purpose_register32():
					new_instructions.append(instruction)
			elif isinstance(instruction, SseMovInstruction):
				if instruction.destination != instruction.source:
					new_instructions.append(instruction)
			elif isinstance(instruction, AvxMovInstruction):
				if instruction.destination != instruction.source:
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
		return list(isa_extensions)

	def get_yeppp_isa_extensions(self):
		isa_extensions_map = {'CMOV':            ('CMOV',       None,            None),
		                      'MMX':             ( None,       'MMX',           'FPU'),
		                      'MMX+':            ( None,       'MMXPlus',       'FPU'),
		                      '3dnow!':          ( None,       '3dnow',         'FPU'),
		                      '3dnow!+':         ( None,       '3dnowPlus',     'FPU'),
		                      '3dnow! Prefetch': ( None,       '3dnowPrefetch',  None),
		                      'SSE':             ( None,       'SSE',           'XMM'),
		                      'SSE2':            ( None,       'SSE2',          'XMM'),
		                      'SSE3':            ( None,       'SSE3',          'XMM'),
		                      'SSSE3':           ( None,       'SSSE3',         'XMM'),
		                      'SSE4A':           ( None,       'SSE4A',         'XMM'),
		                      'SSE4.1':          ( None,       'SSE4_1',        'XMM'),
		                      'SSE4.2':          ( None,       'SSE4_2',        'XMM'),
		                      'AVX':             ( None,       'AVX',           'YMM'),
		                      'AVX2':            ( None,       'AVX2',          'YMM'),
		                      'FMA3':            ( None,       'FMA3',          'YMM'),
		                      'FMA4':            ( None,       'FMA4',          'YMM'),
		                      'F16C':            ( None,       'F16C',          'YMM'),
		                      'XOP':             ( None,       'XOP',           'YMM'),
		                      'MOVBE':           ('Movbe',      None,            None),
		                      'POPCNT':          ('Popcnt',     None,            None),
		                      'LZCNT':           ('Lzcnt',      None,            None),
		                      'TBM':             ('TBM',        None,            None),
		                      'BMI':             ('BMI',        None,            None),
		                      'BMI2':            ('BMI2',       None,            None),
		                      'TBM':             ('TBM',        None,            None),
		                      'ADX':             ('ADX',        None,            None),
		                      'AES':             ('AES',        None,           'XMM'),
		                      'VAES':            ('AES',        None,           'YMM'),
		                      'RDRAND':          ('Rdrand',     None,            None),
		                      'RDSEED':          ('Rdseed',     None,            None),
		                      'PCLMULQDQ':       ('Pclmulqdq',  None,           'XMM'),
		                      'VPCLMULQDQ':      ('Pclmulqdq',  None,           'YMM')}
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
		isa_extensions = map(lambda id: "YepX86IsaFeature" + id, isa_extensions)
		if not isa_extensions:
			isa_extensions = ["YepIsaFeaturesDefault"]
		simd_extensions = map(lambda id: "YepX86SimdFeature" + id, simd_extensions)
		if not simd_extensions:
			simd_extensions = ["YepSimdFeaturesDefault"]
		system_extensions = map(lambda id: "YepX86SystemFeature" + id, system_extensions)
		if not system_extensions:
			system_extensions = ["YepSystemFeaturesDefault"]
		return (isa_extensions, simd_extensions, system_extensions)

	def allocate_local_variable(self):
		self.local_variables_count += 1
		return self.local_variables_count

	def allocate_avx_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x00C0

	def allocate_sse_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x0040

	def allocate_mmx_register(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x0010

	def allocate_general_purpose_register64(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x000F

	def allocate_general_purpose_register32(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x0007

	def allocate_general_purpose_register16(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x0003

	def allocate_general_purpose_register8(self):
		self.virtual_registers_count += 1
		return (self.virtual_registers_count << 12) | 0x0001

class LocalVariable(object):
	def __init__(self, register_type):
		super(LocalVariable, self).__init__()
		if isinstance(register_type, int):
			self.size = register_type
		elif register_type == GeneralPurposeRegister64:
			self.size = 8
		elif register_type == GeneralPurposeRegister32:
			self.size = 4
		elif register_type == GeneralPurposeRegister16:
			self.size = 2
		elif register_type == GeneralPurposeRegister8:
			self.size = 1
		elif register_type == MMXRegister:
			self.size = 8
		elif register_type == SSERegister:
			self.size = 16
		elif register_type == AVXRegister:
			self.size = 32
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
	# Stack structure:
	# +---------------------------------------------------+
	# | On-stack parameters                               |
	# +---------------------------------------------------+
	# | Return address                                    |
	# +---------------------------------------------------+
	# | Preserved general-purpose registers               |
	# +---------------------------------------------------+
	# | Alignment                                         |
	# +---------------------------------------------------+
	# | Alignment bytes                                   |
	# +---------------------------------------------------+
	# | Preserved SSE registers                           |
	# +---------------------------------------------------+
	# | SSE local variables                               |
	# +---------------------------------------------------+
	# | AVX local variables                               |
	# +---------------------------------------------------+
	def __init__(self, abi):
		super(StackFrame, self).__init__()
		self.abi = abi
		self.general_purpose_registers = list()
		self.sse_registers = list()
		self.sse_variables = list()
		self.avx_variables = list()

	def preserve_registers(self, registers):
		for register in registers:
			self.preserve_register(register)

	def preserve_register(self, register):
		if isinstance(register, GeneralPurposeRegister8):
			register = register.get_qword()
		elif isinstance(register, GeneralPurposeRegister16):
			register = register.get_qword()
		elif isinstance(register, GeneralPurposeRegister32):
			register = register.get_qword()
		elif isinstance(register, AVXRegister):
			register = register.get_oword()

		if not register in self.abi.callee_save_registers:
			return

		if isinstance(register, GeneralPurposeRegister64):
			if not register in self.general_purpose_registers:
				self.general_purpose_registers.append(register)
		elif isinstance(register, SSERegister):
			if not register in self.sse_registers:
				self.sse_registers.append(register)
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

	def get_parameters_address(self, use_rbp):
		if use_rbp:
			return rbp + 8
		else:
			parameters_offset = len(self.general_purpose_registers) * 8 + len(self.sse_registers) * 16 + len(self.sse_variables) * 16
			if len(self.general_purpose_registers) % 2 == 0:
				parameters_offset += 8
			return rsp + parameters_offset

	def generate_prologue(self, use_avx, use_rbp):
		with InstructionStream() as instructions: 
			# Save general-purpose registers on stack
			if use_rbp:
				PUSH( rbp )
				MOV( rbp, rsp )
			for register in self.general_purpose_registers:
				PUSH( register )
			# This parameters address is valid only is RBP is not used
			self.parameters_address = rsp + len(self.general_purpose_registers) * 8
			variables_size = len(self.sse_variables) * 16 + len(self.avx_variables) * 32
			if len(self.avx_variables) != 0:
				# Align stack on 32
				if use_rbp:
					# Old stack pointer is already preserved in RBP
					AND( rsp, -32 )
				else:
					MOV( rax, rsp )
					SUB( rsp, 8 )
					AND( rsp, -32 )
					MOV( [rsp], rax )
				stack_frame_size = len(self.sse_registers) * 16 + variables_size
				if stack_frame_size % 32 != 0:
					stack_frame_size += 16
				assert stack_frame_size % 32 == 0
				SUB( rsp, stack_frame_size )
			else:
				if len(self.sse_registers) + len(self.sse_variables) != 0:
					# Align stack on 16
					stack_frame_size = len(self.sse_registers) * 16 + variables_size
					if len(self.general_purpose_registers) % 2 == 0:
						stack_frame_size += 8
					SUB( rsp, stack_frame_size )
					self.parameters_address += stack_frame_size
			# Save floating-point registers on stack
			for index, sse_register in enumerate(self.sse_registers):
				if use_avx:
					VMOVAPS( [rsp + variables_size + index * 16], sse_register )
				else:
					MOVAPS( [rsp + variables_size + index * 16], sse_register )
	
			# Assign addresses to local variables
			variable_offset = 0
			for variable in self.avx_variables + self.sse_variables:
				variable.address = rsp + variable_offset
				variable_offset += variable.get_size()
	
			# Fix parameters_address is RBP is used
			if use_rbp:
				self.parameters_address = rbp + 8

		return list(iter(instructions))

	def generate_epilogue(self, use_mmx, use_avx, use_rbp):
		with InstructionStream() as instructions:
			variables_size = len(self.sse_variables) * 16 + len(self.avx_variables) * 32
			# Restore floating-point registers from stack
			for index, sse_register in enumerate(self.sse_registers):
				if use_avx:
					VMOVAPS( sse_register, [rsp + variables_size + index * 16] )
				else:
					MOVAPS( sse_register, [rsp + variables_size + index * 16] )
	
			if use_rbp:
				MOV( rsp, rbp )
				POP( rbp )
			else:
				# Restore stack pointer
				if len(self.avx_variables) != 0:
					stack_frame_size = len(self.sse_registers) * 16 + variables_size
					if stack_frame_size % 32 != 0:
						stack_frame_size += 16
		
					MOV( rsp, [rsp + stack_frame_size] )
				else:
					if len(self.sse_registers) + len(self.sse_variables) != 0:
						stack_frame_size = len(self.sse_registers) * 16 + variables_size
						if len(self.general_purpose_registers) % 2 == 0:
							stack_frame_size += 8
						ADD( rsp, stack_frame_size )
	
			# Restore general-purpose registers from stack
			for register in reversed(self.general_purpose_registers):
				POP( register )
			if use_mmx:
				EMMS()
			if use_avx:
				VZEROUPPER()

		return list(iter(instructions))

class Register(object):
	GPType  = 1
	MMXType = 2
	AVXType = 3
	
	def __init__(self):
		super(Register, self).__init__()

	def __lt__(self, other):
		return self.number < other.number

	def __le__(self, other):
		return self.number <= other.number

	def __eq__(self, other):
		if isinstance(other, Register):
			return self.number == other.number
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, Register):
			return self.number != other.number
		else:
			return True

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

	@staticmethod
	def from_parts(id, mask):
		# Mask not necessarily is valid, e.g. it can include only the high part of a 32-bit register
		assert mask != 0
		if (mask & ~0x00F) == 0:
			# General-purpose register
			if (mask & 0x8) == 0x8:
				return GeneralPurposeRegister64((id << 12) | 0x00F)
			elif (mask & 0x4) == 0x4:
				return GeneralPurposeRegister32((id << 12) | 0x007)
			elif (mask & 0x3) == 0x3:
				return GeneralPurposeRegister16((id << 12) | 0x003)
			else:
				return GeneralPurposeRegister8((id << 12) | mask)
		elif (mask & ~0x010) == 0:
			# MMX register
			return MMXRegister((id << 12) | 0x010)
		elif (mask & ~0x0C0) == 0:
			# AVX or SSE register
			if (mask & 0x080) == 0x080:
				return AVXRegister((id << 12) | 0x0C0)
			else:
				return SSERegister((id << 12) | 0x040)
		else:
			print mask
			# Unknown register mask
			assert False

	def is_virtual(self):
		return self.number >= 0x40000

	def bind(self, id):
		assert self.is_virtual()
		self.number = (self.number & 0xFFF) | (id << 12)
		assert not self.is_virtual()

class GeneralPurposeRegister(Register):
	def __init__(self):
		super(GeneralPurposeRegister, self).__init__()

class GeneralPurposeRegister64(GeneralPurposeRegister):
	name_to_number_map = {'rax': 0x2000F,
	                      'rbx': 0x2100F,
	                      'rcx': 0x2200F,
	                      'rdx': 0x2300F,
	                      'rsi': 0x2400F,
	                      'rdi': 0x2500F,
	                      'rbp': 0x2600F,
	                      'rsp': 0x2700F,
	                      'r8' : 0x2800F,
	                      'r9' : 0x2900F,
	                      'r10': 0x2A00F,
	                      'r11': 0x2B00F,
	                      'r12': 0x2C00F,
	                      'r13': 0x2D00F,
	                      'r14': 0x2E00F,
	                      'r15': 0x2F00F}

	number_to_name_map = {0x2000F: 'rax',
	                      0x2100F: 'rbx',
	                      0x2200F: 'rcx',
	                      0x2300F: 'rdx',
	                      0x2400F: 'rsi',
	                      0x2500F: 'rdi',
	                      0x2600F: 'rbp',
	                      0x2700F: 'rsp',
	                      0x2800F: 'r8',
	                      0x2900F: 'r9',
	                      0x2A00F: 'r10',
	                      0x2B00F: 'r11',
	                      0x2C00F: 'r12',
	                      0x2D00F: 'r13',
	                      0x2E00F: 'r14',
	                      0x2F00F: 'r15'}

	def __init__(self, id = None):
		super(GeneralPurposeRegister64, self).__init__()
		if id is None:
			self.number = current_function.allocate_general_purpose_register64()
			self.type = Register.GPType
			self.size = 8
		elif isinstance(id, int):
			self.number = id
			self.type = Register.GPType
			self.size = 8
		elif isinstance(id, str):
			if id in GeneralPurposeRegister64.name_to_number_map.iterkeys():
				self.number = GeneralPurposeRegister64.name_to_number_map[id]
				self.type = Register.GPType
				self.size = 8
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, GeneralPurposeRegister64):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id  is neither a name of an architectural general-purpose 64-bit register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'gp64-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return GeneralPurposeRegister64.number_to_name_map[self.number]

	def __add__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64WithOffset(self, offset)
		elif isinstance(offset, ScaledGeneralPurposeRegister64):
			return GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64(self, offset.register, offset.scale)
		else:
			raise TypeError('Offset is not an integer')

	def __sub__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64WithOffset(self, -offset)
		else:
			raise TypeError('Offset is not an integer')

	def __mul__(self, scale):
		if isinstance(scale, int):
			if scale in [1, 2, 4, 8]:
				return ScaledGeneralPurposeRegister64(self, scale)
			else:
				raise TypeError('Invalid scale number {0}: only scaling by 1, 2, 4, or 8 is supported on x86'.format(scale))
		else:
			return TypeError('Scale is not an integer')

	def is_extended(self):
		return self.number >= 0x28000

	def get_low_byte(self):
		return GeneralPurposeRegister8((self.number & -16) | 0x0001)

	def get_word(self):
		return GeneralPurposeRegister16((self.number & -16) | 0x0003)

	def get_dword(self):
		return GeneralPurposeRegister32((self.number & -16) | 0x0007)

	def get_qword(self):
		return GeneralPurposeRegister64((self.number & -16) | 0x000F)

rax = GeneralPurposeRegister64('rax')
rbx = GeneralPurposeRegister64('rbx')
rcx = GeneralPurposeRegister64('rcx')
rdx = GeneralPurposeRegister64('rdx')
rsi = GeneralPurposeRegister64('rsi')
rdi = GeneralPurposeRegister64('rdi')
rbp = GeneralPurposeRegister64('rbp')
rsp = GeneralPurposeRegister64('rsp')
r8  = GeneralPurposeRegister64('r8')
r9  = GeneralPurposeRegister64('r9')
r10 = GeneralPurposeRegister64('r10')
r11 = GeneralPurposeRegister64('r11')
r12 = GeneralPurposeRegister64('r12')
r13 = GeneralPurposeRegister64('r13')
r14 = GeneralPurposeRegister64('r14')
r15 = GeneralPurposeRegister64('r15')

class GeneralPurposeRegister64WithOffset(object):
	def __init__(self, register, offset):
		super(GeneralPurposeRegister64WithOffset, self).__init__()
		self.register = register
		self.offset = offset
		if not isinstance(register, GeneralPurposeRegister64):
			raise TypeError('Register is not an instance of the 64-bit general-purpose register clas')
		if not isinstance(offset, int):
			raise TypeError('Offset is not an integer')

	def __add__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64WithOffset(self.register, self.offset + offset)
		else:
			raise TypeError('Offset is not an integer')

	def __sub__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64WithOffset(self.register, self.offset - offset)
		else:
			raise TypeError('Offset is not an integer')

	def __str__(self):
		if self.offset == 0:
			return str(self.register)
		elif self.offset > 0:
			return "{0} + {1}".format(self.register, self.offset)
		else:
			return "{0} - {1}".format(self.register, -self.offset)

class ScaledGeneralPurposeRegister64(object):
	def __init__(self, register, scale):
		super(ScaledGeneralPurposeRegister64, self).__init__()
		self.register = register
		self.scale = scale
		if not isinstance(register, GeneralPurposeRegister64):
			raise TypeError('Register is not an instance of the 64-bit general-purpose register clas')
		if not isinstance(scale, int):
			raise TypeError('Scale is not an integer')

	def __str__(self):
		return "{0} * {1}".format(self.register, self.scale)

class GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64(object):
	def __init__(self, base, index, scale):
		super(GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64, self).__init__()
		self.base = base
		self.index = index
		self.scale = scale
		if not isinstance(base, GeneralPurposeRegister64):
			raise TypeError('Base register is not an instance of the 64-bit general-purpose register clas')
		if not isinstance(index, GeneralPurposeRegister64):
			raise TypeError('Index register is not an instance of the 64-bit general-purpose register clas')
		if not isinstance(scale, int):
			raise TypeError('Scale is not an integer')

	def __str__(self):
		return "{0} + {1} * {2}".format(self.base, self.index, self.scale)

	def __add__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset(self.base, self.index, self.scale, offset)
		else:
			raise TypeError('Offset is not an integer')

	def __sub__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset(self.base, self.index, self.scale, -offset)
		else:
			raise TypeError('Offset is not an integer')

class GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset(object):
	def __init__(self, base, index, scale, offset):
		super(GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset, self).__init__()
		self.base = base
		self.index = index
		self.scale = scale
		self.offset = offset
		if not isinstance(base, GeneralPurposeRegister64):
			raise TypeError('Base register is not an instance of the 64-bit general-purpose register clas')
		if not isinstance(index, GeneralPurposeRegister64):
			raise TypeError('Index register is not an instance of the 64-bit general-purpose register clas')
		if not isinstance(scale, int):
			raise TypeError('Scale is not an integer')
		if not isinstance(offset, int):
			raise TypeError('Offset is not an integer')

	def __str__(self):
		if self.offset == 0:
			return "{0} + {1} * {2}".format(self.base, self.index, self.scale)
		elif self.offset > 0:
			return "{0} + {1} * {2} + {3}".format(self.base, self.index, self.scale, self.offset)
		else:
			return "{0} + {1} * {2} - {3}".format(self.base, self.index, self.scale, -self.offset)

	def __add__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset(self.base, self.index, self.scale, self.offset + offset)
		else:
			raise TypeError('Offset is not an integer')

	def __sub__(self, offset):
		if isinstance(offset, int):
			return GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset(self.base, self.index, self.scale, self.offset - offset)
		else:
			raise TypeError('Offset is not an integer')

class GeneralPurposeRegister32(GeneralPurposeRegister):
	name_to_number_map = {'eax' : 0x20007,
	                      'ebx' : 0x21007,
	                      'ecx' : 0x22007,
	                      'edx' : 0x23007,
	                      'esi' : 0x24007,
	                      'edi' : 0x25007,
	                      'ebp' : 0x26007,
	                      'esp' : 0x27007,
	                      'r8d' : 0x28007,
	                      'r9d' : 0x29007,
	                      'r10d': 0x2A007,
	                      'r11d': 0x2B007,
	                      'r12d': 0x2C007,
	                      'r13d': 0x2D007,
	                      'r14d': 0x2E007,
	                      'r15d': 0x2F007}

	number_to_name_map = {0x20007: 'eax',
	                      0x21007: 'ebx',
	                      0x22007: 'ecx',
	                      0x23007: 'edx',
	                      0x24007: 'esi',
	                      0x25007: 'edi',
	                      0x26007: 'ebp',
	                      0x27007: 'esp',
	                      0x28007: 'r8d',
	                      0x29007: 'r9d',
	                      0x2A007: 'r10d',
	                      0x2B007: 'r11d',
	                      0x2C007: 'r12d',
	                      0x2D007: 'r13d',
	                      0x2E007: 'r14d',
	                      0x2F007: 'r15d'}

	def __init__(self, id = None):
		super(GeneralPurposeRegister32, self).__init__()
		if id is None:
			self.number = current_function.allocate_general_purpose_register32()
			self.type = Register.GPType
			self.size = 4
		elif isinstance(id, int):
			self.number = id
			self.type = Register.GPType
			self.size = 4
		elif isinstance(id, str):
			if id in GeneralPurposeRegister32.name_to_number_map.iterkeys():
				self.number = GeneralPurposeRegister32.name_to_number_map[id]
				self.type = Register.GPType
				self.size = 4
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, GeneralPurposeRegister32):
			self.number = id.number
			self.type = id.type
			self.bsize = id.bsize
		else:
			raise TypeError('Register id is neither a name of an architectural general-purpose 32-bit register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'gp32-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return GeneralPurposeRegister32.number_to_name_map[self.number]

	def is_extended(self):
		return self.number >= 0x28000

	def get_low_byte(self):
		return GeneralPurposeRegister8((self.number & -16) | 0x0001)

	def get_word(self):
		return GeneralPurposeRegister16((self.number & -16) | 0x0003)

	def get_dword(self):
		return GeneralPurposeRegister32((self.number & -16) | 0x0007)

	def get_qword(self):
		return GeneralPurposeRegister64((self.number & -16) | 0x000F)

eax  = GeneralPurposeRegister32('eax')
ebx  = GeneralPurposeRegister32('ebx')
ecx  = GeneralPurposeRegister32('ecx')
edx  = GeneralPurposeRegister32('edx')
esi  = GeneralPurposeRegister32('esi')
edi  = GeneralPurposeRegister32('edi')
ebp  = GeneralPurposeRegister32('ebp')
r8d  = GeneralPurposeRegister32('r8d')
r9d  = GeneralPurposeRegister32('r9d')
r10d = GeneralPurposeRegister32('r10d')
r11d = GeneralPurposeRegister32('r11d')
r12d = GeneralPurposeRegister32('r12d')
r13d = GeneralPurposeRegister32('r13d')
r14d = GeneralPurposeRegister32('r14d')
r15d = GeneralPurposeRegister32('r15d')

class GeneralPurposeRegister16(GeneralPurposeRegister):
	name_to_number_map = {'ax'  : 0x20003,
	                      'bx'  : 0x21003,
	                      'cx'  : 0x22003,
	                      'dx'  : 0x23003,
	                      'si'  : 0x24003,
	                      'di'  : 0x25003,
	                      'bp'  : 0x26003,
	                      'sp'  : 0x27003,
	                      'r8w' : 0x28003,
	                      'r9w' : 0x29003,
	                      'r10w': 0x2A003,
	                      'r11w': 0x2B003,
	                      'r12w': 0x2C003,
	                      'r13w': 0x2D003,
	                      'r14w': 0x2E003,
	                      'r15w': 0x2F003}

	number_to_name_map = {0x20003: 'ax',
	                      0x21003: 'bx',
	                      0x22003: 'cx',
	                      0x23003: 'dx',
	                      0x24003: 'si',
	                      0x25003: 'di',
	                      0x26003: 'bp',
	                      0x27003: 'sp',
	                      0x28003: 'r8w',
	                      0x29003: 'r9w',
	                      0x2A003: 'r10w',
	                      0x2B003: 'r11w',
	                      0x2C003: 'r12w',
	                      0x2D003: 'r13w',
	                      0x2E003: 'r14w',
	                      0x2F003: 'r15w'}

	def __init__(self, id = None):
		super(GeneralPurposeRegister16, self).__init__()
		if id is None:
			self.number = current_function.allocate_general_purpose_register16()
			self.type = Register.GPType
			self.size = 2
		elif isinstance(id, int):
			self.number = id
			self.type = Register.GPType
			self.size = 2
		elif isinstance(id, str):
			if id in GeneralPurposeRegister16.name_to_number_map.iterkeys():
				self.number = GeneralPurposeRegister16.name_to_number_map[id]
				self.type = Register.GPType
				self.size = 2
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, GeneralPurposeRegister16):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural general-purpose 16-bit register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'gp16-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return GeneralPurposeRegister16.number_to_name_map[self.number]

	def is_extended(self):
		return self.number >= 0x28000

	def get_low_byte(self):
		return GeneralPurposeRegister8((self.number & -16) | 0x0001)

	def get_word(self):
		return GeneralPurposeRegister16((self.number & -16) | 0x0003)

	def get_dword(self):
		return GeneralPurposeRegister32((self.number & -16) | 0x0007)

	def get_qword(self):
		return GeneralPurposeRegister64((self.number & -16) | 0x000F)

ax   = GeneralPurposeRegister16('ax')
bx   = GeneralPurposeRegister16('bx')
cx   = GeneralPurposeRegister16('cx')
dx   = GeneralPurposeRegister16('dx')
si   = GeneralPurposeRegister16('si')
di   = GeneralPurposeRegister16('di')
bp   = GeneralPurposeRegister16('bp')
r8w  = GeneralPurposeRegister16('r8w')
r9w  = GeneralPurposeRegister16('r9w')
r10w = GeneralPurposeRegister16('r10w')
r11w = GeneralPurposeRegister16('r11w')
r12w = GeneralPurposeRegister16('r12w')
r13w = GeneralPurposeRegister16('r13w')
r14w = GeneralPurposeRegister16('r14w')
r15w = GeneralPurposeRegister16('r15w')

class GeneralPurposeRegister8(GeneralPurposeRegister):
	name_to_number_map = {'al'  : 0x20001,
	                      'ah'  : 0x20002,
	                      'bl'  : 0x21001,
	                      'bh'  : 0x21002,
	                      'cl'  : 0x22001,
	                      'ch'  : 0x22002,
	                      'dl'  : 0x23001,
	                      'dh'  : 0x23002,
	                      'sil' : 0x24001,
	                      'dil' : 0x25001,
	                      'bpl' : 0x26001,
	                      'spl' : 0x27001,
	                      'r8b' : 0x28001,
	                      'r9b' : 0x29001,
	                      'r10b': 0x2A001,
	                      'r11b': 0x2B001,
	                      'r12b': 0x2C001,
	                      'r13b': 0x2D001,
	                      'r14b': 0x2E001,
	                      'r15b': 0x2F001}

	number_to_name_map = {0x20001: 'al',
	                      0x20002: 'ah',
	                      0x21001: 'bl',
	                      0x21002: 'bh',
	                      0x22001: 'cl',
	                      0x22002: 'ch',
	                      0x23001: 'dl',
	                      0x23002: 'dh',
	                      0x24001: 'sil',
	                      0x25001: 'dil',
	                      0x26001: 'bpl',
	                      0x27001: 'spl',
	                      0x28001: 'r8b',
	                      0x29001: 'r9b',
	                      0x2A001: 'r10b',
	                      0x2B001: 'r11b',
	                      0x2C001: 'r12b',
	                      0x2D001: 'r13b',
	                      0x2E001: 'r14b',
	                      0x2F001: 'r15b'}

	def __init__(self, id = None):
		super(GeneralPurposeRegister8, self).__init__()
		if id is None:
			self.number = current_function.allocate_general_purpose_register8()
			self.type = Register.GPType
			self.size = 1
		elif isinstance(id, int):
			self.number = id
			self.type = Register.GPType
			self.size = 1
		elif isinstance(id, str):
			if id in GeneralPurposeRegister8.name_to_number_map.iterkeys():
				self.number = GeneralPurposeRegister8.name_to_number_map[id]
				self.type = Register.GPType
				self.size = 1
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, GeneralPurposeRegister8):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural general-purpose 8-bit register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'gp8-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return GeneralPurposeRegister8.number_to_name_map[self.number]

	def is_extended(self):
		return self.number >= 0x28000

	def get_low_byte(self):
		return GeneralPurposeRegister8((self.number & -16) | 0x0001)

	def get_word(self):
		return GeneralPurposeRegister16((self.number & -16) | 0x0003)

	def get_dword(self):
		return GeneralPurposeRegister32((self.number & -16) | 0x0007)

	def get_qword(self):
		return GeneralPurposeRegister64((self.number & -16) | 0x000F)

al   = GeneralPurposeRegister8('al')
ah   = GeneralPurposeRegister8('ah')
bl   = GeneralPurposeRegister8('bl')
bh   = GeneralPurposeRegister8('bh')
cl   = GeneralPurposeRegister8('cl')
ch   = GeneralPurposeRegister8('ch')
dl   = GeneralPurposeRegister8('dl')
dh   = GeneralPurposeRegister8('dh')
sil  = GeneralPurposeRegister8('sil')
dil  = GeneralPurposeRegister8('dil')
bpl  = GeneralPurposeRegister8('bpl')
r8b  = GeneralPurposeRegister8('r8b')
r9b  = GeneralPurposeRegister8('r9b')
r10b = GeneralPurposeRegister8('r10b')
r11b = GeneralPurposeRegister8('r11b')
r12b = GeneralPurposeRegister8('r12b')
r13b = GeneralPurposeRegister8('r13b')
r14b = GeneralPurposeRegister8('r14b')
r15b = GeneralPurposeRegister8('r15b')

class MMXRegister(Register):
	name_to_number_map = {'mm0': 0x10010,
	                      'mm1': 0x11010,
	                      'mm2': 0x12010,
	                      'mm3': 0x13010,
	                      'mm4': 0x14010,
	                      'mm5': 0x15010,
	                      'mm6': 0x16010,
	                      'mm7': 0x17010}

	number_to_name_map = {0x10010: 'mm0',
	                      0x11010: 'mm1',
	                      0x12010: 'mm2',
	                      0x13010: 'mm3',
	                      0x14010: 'mm4',
	                      0x15010: 'mm5',
	                      0x16010: 'mm6',
	                      0x17010: 'mm7'}

	def __init__(self, id = None):
		super(MMXRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_mmx_register()
			self.type = Register.MMXType
			self.size = 8
		elif isinstance(id, int):
			self.number = id
			self.type = Register.MMXType
			self.size = 8
		elif isinstance(id, str):
			if id in MMXRegister.name_to_number_map.iterkeys():
				self.number = MMXRegister.name_to_number_map[id]
				self.type = Register.MMXType
				self.size = 8
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, MMXRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural mmx register, nor an id of a virtual register')

	def __str__(self):
		if self.is_virtual():
			return 'mm-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return MMXRegister.number_to_name_map[self.number]

mm0 = MMXRegister('mm0')
mm1 = MMXRegister('mm1')
mm2 = MMXRegister('mm2')
mm3 = MMXRegister('mm3')
mm4 = MMXRegister('mm4')
mm5 = MMXRegister('mm5')
mm6 = MMXRegister('mm6')
mm7 = MMXRegister('mm7')

class SSERegister(Register):
	name_to_number_map = {'xmm0' : 0x00040,
	                      'xmm1' : 0x01040,
	                      'xmm2' : 0x02040,
	                      'xmm3' : 0x03040,
	                      'xmm4' : 0x04040,
	                      'xmm5' : 0x05040,
	                      'xmm6' : 0x06040,
	                      'xmm7' : 0x07040,
	                      'xmm8' : 0x08040,
	                      'xmm9' : 0x09040,
	                      'xmm10': 0x0A040,
	                      'xmm11': 0x0B040,
	                      'xmm12': 0x0C040,
	                      'xmm13': 0x0D040,
	                      'xmm14': 0x0E040,
	                      'xmm15': 0x0F040}

	number_to_name_map = {0x00040: 'xmm0',
	                      0x01040: 'xmm1',
	                      0x02040: 'xmm2',
	                      0x03040: 'xmm3',
	                      0x04040: 'xmm4',
	                      0x05040: 'xmm5',
	                      0x06040: 'xmm6',
	                      0x07040: 'xmm7',
	                      0x08040: 'xmm8',
	                      0x09040: 'xmm9',
	                      0x0A040: 'xmm10',
	                      0x0B040: 'xmm11',
	                      0x0C040: 'xmm12',
	                      0x0D040: 'xmm13',
	                      0x0E040: 'xmm14',
	                      0x0F040: 'xmm15'}

	def __init__(self, id = None):
		super(SSERegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_sse_register()
			self.type = Register.AVXType
			self.size = 16
		elif isinstance(id, int):
			self.number = id
			self.type = Register.AVXType
			self.size = 16
		elif isinstance(id, str):
			if id in SSERegister.name_to_number_map.iterkeys():
				self.number = SSERegister.name_to_number_map[id]
				self.type = Register.AVXType
				self.size = 16
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, SSERegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural sse register, nor an id of a virtual register')

	def is_extended(self):
		return self.number >= 0x08000

	def __str__(self):
		if self.is_virtual():
			return 'xmm-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return SSERegister.number_to_name_map[self.number]

	def get_oword(self):
		return SSERegister((self.number & -256) | 0x0040)

	def get_hword(self):
		return AVXRegister((self.number & -256) | 0x00C0)

xmm0  = SSERegister('xmm0')
xmm1  = SSERegister('xmm1')
xmm2  = SSERegister('xmm2')
xmm3  = SSERegister('xmm3')
xmm4  = SSERegister('xmm4')
xmm5  = SSERegister('xmm5')
xmm6  = SSERegister('xmm6')
xmm7  = SSERegister('xmm7')
xmm8  = SSERegister('xmm8')
xmm9  = SSERegister('xmm9')
xmm10 = SSERegister('xmm10')
xmm11 = SSERegister('xmm11')
xmm12 = SSERegister('xmm12')
xmm13 = SSERegister('xmm13')
xmm14 = SSERegister('xmm14')
xmm15 = SSERegister('xmm15')

class AVXRegister(Register):
	name_to_number_map = {'ymm0' : 0x000C0,
	                      'ymm1' : 0x010C0,
	                      'ymm2' : 0x020C0,
	                      'ymm3' : 0x030C0,
	                      'ymm4' : 0x040C0,
	                      'ymm5' : 0x050C0,
	                      'ymm6' : 0x060C0,
	                      'ymm7' : 0x070C0,
	                      'ymm8' : 0x080C0,
	                      'ymm9' : 0x090C0,
	                      'ymm10': 0x0A0C0,
	                      'ymm11': 0x0B0C0,
	                      'ymm12': 0x0C0C0,
	                      'ymm13': 0x0D0C0,
	                      'ymm14': 0x0E0C0,
	                      'ymm15': 0x0F0C0}

	number_to_name_map = {0x000C0: 'ymm0',
	                      0x010C0: 'ymm1',
	                      0x020C0: 'ymm2',
	                      0x030C0: 'ymm3',
	                      0x040C0: 'ymm4',
	                      0x050C0: 'ymm5',
	                      0x060C0: 'ymm6',
	                      0x070C0: 'ymm7',
	                      0x080C0: 'ymm8',
	                      0x090C0: 'ymm9',
	                      0x0A0C0: 'ymm10',
	                      0x0B0C0: 'ymm11',
	                      0x0C0C0: 'ymm12',
	                      0x0D0C0: 'ymm13',
	                      0x0E0C0: 'ymm14',
	                      0x0F0C0: 'ymm15'}

	def __init__(self, id = None):
		super(AVXRegister, self).__init__()
		if id is None:
			self.number = current_function.allocate_avx_register()
			self.type = Register.AVXType
			self.size = 32
		elif isinstance(id, int):
			self.number = id
			self.type = Register.AVXType
			self.size = 32
		elif isinstance(id, str):
			if id in AVXRegister.name_to_number_map.iterkeys():
				self.number = AVXRegister.name_to_number_map[id]
				self.type = Register.AVXType
				self.size = 32
			else:
				raise ValueError('Unknown register name: {0}'.format(id))
		elif isinstance(id, AVXRegister):
			self.number = id.number
			self.type = id.type
			self.size = id.size
		else:
			raise TypeError('Register id is neither a name of an architectural sse register, nor an id of a virtual register')

	def is_extended(self):
		return self.number >= 0x08000

	def __str__(self):
		if self.is_virtual():
			return 'ymm-vreg<{0}>'.format((self.number - 0x40000) >> 12)
		else:
			return AVXRegister.number_to_name_map[self.number]

	def get_oword(self):
		return SSERegister((self.number & -256) | 0x0040)

	def get_hword(self):
		return AVXRegister((self.number & -256) | 0x00C0)

ymm0  = AVXRegister('ymm0')
ymm1  = AVXRegister('ymm1')
ymm2  = AVXRegister('ymm2')
ymm3  = AVXRegister('ymm3')
ymm4  = AVXRegister('ymm4')
ymm5  = AVXRegister('ymm5')
ymm6  = AVXRegister('ymm6')
ymm7  = AVXRegister('ymm7')
ymm8  = AVXRegister('ymm8')
ymm9  = AVXRegister('ymm9')
ymm10 = AVXRegister('ymm10')
ymm11 = AVXRegister('ymm11')
ymm12 = AVXRegister('ymm12')
ymm13 = AVXRegister('ymm13')
ymm14 = AVXRegister('ymm14')
ymm15 = AVXRegister('ymm15')

class Operand(object):
	RegisterType = 1
	ImmediateType = 2
	MemoryType = 3
	ConstantType = 4
	VariableType = 5
	LabelType = 6
	NoneType = 7
	
	def __init__(self, operand):
		super(Operand, self).__init__()
		if isinstance(operand, Register):
			import copy
			self.type = Operand.RegisterType
			self.register = copy.deepcopy(operand)
		elif isinstance(operand, int) or isinstance(operand, long):
			if -9223372036854775808L <= operand <= 18446744073709551615L:
				self.type = Operand.ImmediateType
				self.immediate = operand
			else:
				raise ValueError('The immediate operand {0} is not a 64-bit value'.format(operand))
		elif isinstance(operand, list):
			if len(operand) == 1:
				address = operand[0]
				self.type = Operand.MemoryType
				self.size = None
				if isinstance(address, GeneralPurposeRegister64):
					self.base = address
					self.scale = 0
					self.index = None
					self.offset = 0
				elif isinstance(address, GeneralPurposeRegister64WithOffset):
					self.base = address.register
					self.scale = 0
					self.index = None
					self.offset = address.offset
				elif isinstance(address, ScaledGeneralPurposeRegister64):
					self.base = None
					self.scale = address.scale
					self.index = address.register
					self.offset = 0
				elif isinstance(address, GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64):
					self.base = address.base
					self.scale = address.scale
					self.index = address.index
					self.offset = 0
				elif isinstance(address, GeneralPurposeRegister64PlusScaledGeneralPurposeRegister64WithOffset):
					self.base = address.base
					self.scale = address.scale
					self.index = address.index
					self.offset = address.offset
				else:
					raise TypeError('Memory operand must be a list with register or register + offset')
			else:
				raise ValueError('Memory operand must be a list with only one element')
		elif isinstance(operand, MemoryOperand):
			address = operand.address
			self.type = Operand.MemoryType
			self.size = operand.size
			if isinstance(address, GeneralPurposeRegister64):
				self.base = address
				self.scale = 0
				self.index = None
				self.offset = 0
			elif isinstance(address, GeneralPurposeRegister64WithOffset):
				self.base = address.register
				self.scale = 0
				self.index = None
				self.offset = address.offset
			else:
				raise TypeError('Memory operand must be a list with register or register + offset')
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
			size_specifier = MemoryOperandSizeSpecifier.size_to_name_map[self.size]
			if self.constant.prefix is None:
				return size_specifier + "[rel {0}]".format(self.constant.label)
			else:
				return size_specifier + "[rel {1}.{0}]".format(self.constant.label, self.constant.prefix)
		elif self.is_local_variable():
			size_specifier = MemoryOperandSizeSpecifier.size_to_name_map[self.size] + " "
			return size_specifier + str(self.variable)
		elif self.is_memory_address():
			size_specifier = ""
			if not self.size is None:
				size_specifier = MemoryOperandSizeSpecifier.size_to_name_map[self.size] + " "
			if self.offset == 0:
				offset_prefix = "" 
			elif -128 <= self.offset <= 127:
				offset_prefix = "byte "
			else:
				offset_prefix = "dword "
			if self.base and self.index:
				address_string = offset_prefix + str(self.base) + " + " + str(self.index) + " * " + str(self.scale)
			elif self.base: 
				address_string = offset_prefix + str(self.base)
			elif self.index:
				address_string = offset_prefix + str(self.index) + " * " + str(self.scale)
			if self.offset > 0:
				address_string = address_string + " + " + str(self.offset) 
			elif self.offset < 0: 
				address_string = address_string + " - " + str(-self.offset) 
			return size_specifier + "[" + address_string + "]"
		elif self.is_register():
			return str(self.register)
		elif self.is_label():
			return self.label
		elif self.is_immediate():
			return str(self.immediate)
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

	def is_int64(self):
		return self.type == Operand.ImmediateType

	def is_int32(self):
		return self.type == Operand.ImmediateType and -2147483648 <= self.immediate <= 4294967295

	def is_sint32(self):
		return self.type == Operand.ImmediateType and -2147483648 <= self.immediate <= 2147483647

	def is_int16(self):
		return self.type == Operand.ImmediateType and -32768 <= self.immediate <= 65535

	def is_uint16(self):
		return self.type == Operand.ImmediateType and 0 <= self.immediate <= 65535

	def is_int8(self):
		return self.type == Operand.ImmediateType and -128 <= self.immediate <= 255

	def is_uint8(self):
		return self.type == Operand.ImmediateType and 0 <= self.immediate <= 255

	def is_sint8(self):
		return self.type == Operand.ImmediateType and -128 <= self.immediate <= 127

	def is_label(self):
		return self.type == Operand.LabelType

	def is_constant(self):
		return self.type == Operand.ConstantType

	def is_local_variable(self):
		return self.type == Operand.VariableType

	def is_register(self):
		return self.type == Operand.RegisterType

	def is_general_purpose_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, GeneralPurposeRegister)

	def is_general_purpose_register64(self):
		return self.type == Operand.RegisterType and isinstance(self.register, GeneralPurposeRegister64)

	def is_general_purpose_register32(self):
		return self.type == Operand.RegisterType and isinstance(self.register, GeneralPurposeRegister32)

	def is_general_purpose_register16(self):
		return self.type == Operand.RegisterType and isinstance(self.register, GeneralPurposeRegister16)

	def is_general_purpose_register8(self):
		return self.type == Operand.RegisterType and isinstance(self.register, GeneralPurposeRegister8)

	def is_mmx_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, MMXRegister)

	def is_sse_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, SSERegister)

	def is_avx_register(self):
		return self.type == Operand.RegisterType and isinstance(self.register, AVXRegister)

	def is_memory_address(self):
		return self.type == Operand.MemoryType or self.type == Operand.ConstantType or self.type == Operand.VariableType

	def is_memory_address256(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 256
		elif self.type == Operand.ConstantType:
			return self.size == 256
		elif self.type == Operand.VariableType:
			return self.size == 256
		else:
			return False

	def is_memory_address128(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 128
		elif self.type == Operand.ConstantType:
			return self.size == 128
		elif self.type == Operand.VariableType:
			return self.size == 128
		else:
			return False

	def is_memory_address80(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 80
		elif self.type == Operand.ConstantType:
			return self.size == 80
		else:
			return False

	def is_memory_address64(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 64
		elif self.type == Operand.ConstantType:
			if strict_size:
				return self.size == 64
			else:
				return True
		elif self.type == Operand.VariableType:
			if strict_size:
				return self.size == 64
			else:
				return True
		else:
			return False

	def is_memory_address32(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 32
		elif self.type == Operand.ConstantType:
			if strict_size:
				return self.size == 32
			else:
				return True
		elif self.type == Operand.VariableType:
			if strict_size:
				return self.size == 32
			else:
				return True
		else:
			return False

	def is_memory_address16(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 16
		elif self.type == Operand.ConstantType:
			if strict_size:
				return self.size == 16
			else:
				return True
		elif self.type == Operand.VariableType:
			if strict_size:
				return self.size == 16
			else:
				return True
		else:
			return False

	def is_memory_address8(self, strict_size = False):
		if self.type == Operand.MemoryType:
			if self.size is None:
				if strict_size:
					return False
				else:
					return True
			else:
				return self.size == 8
		elif self.type == Operand.ConstantType:
			if strict_size:
				return self.size == 8
			else:
				return True
		elif self.type == Operand.VariableType:
			if strict_size:
				return self.size == 8
			else:
				return True
		else:
			return False

	def get_modrm_extra_length(self):
		if self.is_register():
			return 0 # encoded in ModR/M, no extra bytes needed
		elif self.is_constant():
			return 4 # 4 bytes for offset
		elif self.is_local_variable():
			return 1 + 4 # rsp-based 32-bit offset
		elif self.is_memory_address():
			if self.offset == 0:
				if self.base == rbp or self.base == r13:
					return 1 # rbp + 0 or r13 + 0 is encoded
				elif self.base == rsp or self.base == r12:
					return 1 # rsp and r12 are encoded in SIB
				else:
					return 0 # encoded in ModR/M, no extra bytes needed
			elif -128 <= self.offset <= 127:
				if self.base == rsp or self.base == r12:
					return 1 + 1 # rsp and r12 Are encoded in SIB + 1 byte for offset
				else:
					return 1 # 1 byte for offset
			else:
				if self.base == rsp or self.base == r12:
					return 4 + 1 # rsp and r12 are encoded in SIB + 4 bytes for offset
				else:
					return 4 # 4 bytes for offset
		else:
			raise ValueError('The operand can not be encoded in ModR/M')

	def get_vex_extra_length(self):
		return 2

	def get_registers_list(self):
		if self.is_register():
			return [self.register]
		elif self.is_constant():
			return list()
		elif self.is_local_variable():
			return [rsp]
		elif self.is_memory_address():
			register_list = list()
			if self.base:
				register_list.append(self.base)
			if self.index:
				register_list.append(self.index)
			return register_list
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
		if isinstance(address, GeneralPurposeRegister64):
			return MemoryOperand(address, self.size)
		elif isinstance(address, GeneralPurposeRegister64WithOffset):
			return MemoryOperand(address, self.size)
		else:
			raise TypeError('Memory address must be either a register or register + offset')

	size_to_name_map = {8: 'byte', 16: 'word', 32: 'dword', 64: '', 80: 'tword', 128: ' ', 256: ' '}


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
			if isinstance(operand[0], GeneralPurposeRegister64):
				return
			elif isinstance(operand[0], GeneralPurposeRegister64WithOffset):
				return
			else:
				raise TypeError('Memory operand must be a list with register or register + offset')
		else:
			raise ValueError('Memory operand must be a list with only one element')
	else:
		return

class QuasiInstruction(object):
	def __init__(self, name, origin = None):
		super(QuasiInstruction, self).__init__()
		self.name = name
		self.line_number = origin[1][2] if origin else None
		self.source_file = origin[1][1] if origin else None
		self.source_code = origin[1][4][0].strip() if origin else None

class Instruction(QuasiInstruction):
	def __init__(self, name, isa_extension = None, origin = None):
		super(Instruction, self).__init__(name, origin = origin)
		if(not isa_extension is None) and (not isa_extension in supported_isa_extensions):
			raise ValueError('Instruction ISA extension {0} in not in the supported ISA extensions list ({1})'.format(isa_extension, ", ".join(supported_isa_extensions)))
		self.isa_extension = isa_extension
		self.short_eax_form = False
		self.always_has_rex_prefix = False
		self.available_registers = set()
		self.live_registers = set()

	def __len__(self):
		return self.size

	def __str__(self):
		return str(self.name)

	def get_isa_extension(self):
		return self.isa_extension

	def is_avx(self):
		if self.isa_extension in ('AVX', 'AVX2', 'FMA4', 'FMA3', 'F16C', 'XOP', 'VAES', 'VPCLMULQDQ'):
			return any(isinstance(register, SSERegister) or isinstance(register, AVXRegister) for register in (self.get_input_registers_list() + self.get_output_registers_list()))
		else:
			return False

	def is_mmx(self):
		if self.isa_extension in ('MMX', 'MMX+', '3dnow!', '3dnow!+'):
			return any(isinstance(register, MMXRegister) for register in (self.get_input_registers_list() + self.get_output_registers_list()))
		else:
			return False

class BinaryInstruction(Instruction):
	def __init__(self, name, destination, source, isa_extension = None, origin = None):
		super(BinaryInstruction, self).__init__(name, isa_extension, origin = origin)
		self.destination = destination
		self.source = source

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

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
		return "." + self.name + ':'

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
		super(LoadParameterPseudoInstruction, self).__init__('<LOAD-PARAMETER>', origin = origin)
		if destination.is_general_purpose_register64():
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
			return [rsp]

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

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

class ArithmeticInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		super(ArithmeticInstruction, self).__init__(name, destination, source, origin = origin)
		allowed_instructions = ['ADD', 'ADC', 'SUB', 'SBB', 'CMP', 'TEST', 'AND', 'OR', 'XOR']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if name != 'TEST' and destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			# ADD r64, r64/m64: REX.W 03 /r
			# ADC r64, r64/m64: REX.W 13 /r
			# SUB r64, r64/m64: REX.W 2B /r
			# SBB r64, r64/m64: REX.W 1B /r
			# CMP r64, r64/m64: REX.W 3B /r
			# AND r64, r64/m64: REX.W 23 /r
			# OR  r64, r64/m64: REX.W 0B /r
			# XOR r64, r64/m64: REX.W 33 /r
			self.size = 1 + 2 + source.get_modrm_extra_length()
			self.always_has_rex_prefix = True
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
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
		elif destination.is_general_purpose_register64() and source.is_sint32():
			if name != 'TEST' and source.is_sint8():
				# ADD r64/m64, imm8: REX.W 83 /0 ib
				# ADC r64/m64, imm8: REX.W 83 /2 ib
				# SUB r64/m64, imm8: REX.W 83 /5 ib
				# SBB r64/m64, imm8: REX.W 83 /3 ib
				# CMP r64/m64, imm8: REX.W 83 /7 ib
				# AND r64/m64, imm8: REX.W 83 /4 ib
				# OR  r64/m64, imm8: REX.W 83 /1 ib
				# XOR r64/m64, imm8: REX.W 83 /6 ib
				self.size = 1 + 2 + 1 + destination.get_modrm_extra_length()
			else:
				if destination == rax:
					# ADD  rax, imm32: REX.W 05 id
					# ADC  rax, imm32: REX.W 15 id
					# SUB  rax, imm32: REX.W 2D id
					# SBB  rax, imm32: REX.W 1D id
					# CMP  rax, imm32: REX.W 3D id
					# AND  rax, imm32: REX.W 25 id
					# OR   rax, imm32: REX.W 0D id
					# XOR  rax, imm32: REX.W 35 id
					# TEST rax, imm32: REX.W A9 id
					self.size = 1 + 1 + 4
				else:
					# ADD  r64/m64, imm32: REX.W 81 /0 id
					# ADC  r64/m64, imm32: REX.W 81 /2 id
					# SUB  r64/m64, imm32: REX.W 81 /5 id
					# SBB  r64/m64, imm32: REX.W 81 /3 id
					# CMP  r64/m64, imm32: REX.W 81 /7 id
					# AND  r64/m64, imm32: REX.W 81 /4 id
					# OR   r64/m64, imm32: REX.W 81 /1 id
					# XOR  r64/m64, imm32: REX.W 81 /6 id
					# TEST r64/m64, imm32: REX.W F7 /0 id
					self.size = 1 + 2 + 4
			self.always_has_rex_prefix = True
			self.short_eax_form = name != 'TEST'
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
		elif name == "TEST" and (destination.is_general_purpose_register64() or destination.is_memory_address64()) and source.is_general_purpose_register64():
			# TEST r64/m64, r64: REX.W + 85 /r
			self.size = 1 + 2 + destination.get_modrm_extra_length()
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

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		elif self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class UnaryArithmeticInstruction(Instruction):
	def __init__(self, name, destination, origin = None):
		super(UnaryArithmeticInstruction, self).__init__(name, origin = origin)
		allowed_instructions = ['NOT', 'NEG', 'INC', 'DEC']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		self.destination = destination
		if destination.is_general_purpose_register64() or destination.is_memory_address64():
			# INC r64/m64: REX.W FF /0
			# DEC r64/m64: REX.W FF /1
			# NOT r64/m64: REX.W F7 /2
			# NEG r64/m64: REX.W F7 /3

			self.size = 1 + 2 + destination.get_modrm_extra_length()
			self.always_has_rex_prefix = True
		elif destination.is_general_purpose_register32() and destination.is_memory_address32():
			# INC r32/m32: FF /0
			# DEC r32/m32: FF /1
			# NOT r32/m32: F7 /2
			# NEG r32/m32: F7 /3

			self.size = 2 + destination.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and destination.is_memory_address16():
			# INC r16/m16: 66 FF /0
			# DEC r16/m16: 66 FF /1
			# NOT r16/m16: 66 F7 /2
			# NEG r16/m16: 66 F7 /3

			self.size = 1 + 2 + destination.get_modrm_extra_length()
		elif destination.is_general_purpose_register8() and destination.is_memory_address8():
			# INC r8/m8: REX.W FE /0
			# DEC r8/m8: REX.W FE /1
			# NOT r8/m8: REX.W F6 /2
			# NEG r8/m8: REX.W F6 /3

			self.size = 1 + 2 + destination.get_modrm_extra_length()
			self.always_has_rex_prefix = True
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format(name, destination))

	def __str__(self):
		return "{0} {1}".format(self.name, self.destination)

	def get_input_registers_list(self):
			return self.destination.get_registers_list()

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class ShiftInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		super(ShiftInstruction, self).__init__(name, destination, source, origin = origin)
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
		elif (destination.is_general_purpose_register64() or destination.is_memory_address64()) and source.is_int8():
			if source.immediate == 1:
				# ROL r64/m64, 1: REX.W D1 /0
				# ROR r64/m64, 1: REX.W D1 /1
				# RCL r64/m64, 1: REX.W D1 /2
				# RCR r64/m64, 1: REX.W D1 /3
				# SHL r64/m64, 1: REX.W D1 /4
				# SHR r64/m64, 1: REX.W D1 /5
				# SAR r64/m64, 1: REX.W D1 /7
				self.size = 1 + 2 + destination.get_modrm_extra_length()
			else:
				# ROL r64/m64, imm8: REX.W C1 /0 ib
				# ROR r64/m64, imm8: REX.W C1 /1 ib
				# RCL r64/m64, imm8: REX.W C1 /2 ib
				# RCR r64/m64, imm8: REX.W C1 /3 ib
				# SHL r64/m64, imm8: REX.W C1 /4 ib
				# SHR r64/m64, imm8: REX.W C1 /5 ib
				# SAR r64/m64, imm8: REX.W C1 /7 ib
				self.size = 1 + 2 + 1 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register8() or destination.is_memory_address8()) and source.is_general_purpose_register():
			if source.register == rcx or source.register == ecx or source.register == cx or source.register == cl or source.register.is_virtual():
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
			if source.register == rcx or source.register == ecx or source.register == cx or source.register == cl or source.register.is_virtual():
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
			if source.register == rcx or source.register == ecx or source.register == cx or source.register == cl or source.register.is_virtual():
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

	def get_constant(self):
		return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class LoadAddressInstruction(Instruction):
	def __init__(self, destination, source, origin = None):
		super(LoadAddressInstruction, self).__init__("LEA", origin = origin)
		if destination.is_general_purpose_register64() and source.is_memory_address():
			# LEAD r64, m: REX.W 8D /r

			self.source = source
			self.destination = destination
			self.size = 1 + 2 + destination.get_modrm_extra_length()
			self.always_has_rex_prefix = True
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format("LEA", destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
			return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class BitTestInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		super(BitTestInstruction, self).__init__(name,  destination, source, origin = origin)
		allowed_instructions = ['BT', 'BTS', 'BTR', 'BTC']
		if name not in allowed_instructions:
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
		if self.destination.is_general_purpose_register() and self.name != "BT":
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class ImulInstruction(Instruction):
	def __init__(self, destination, source, immediate, origin = None):
		super(ImulInstruction, self).__init__("IMUL", origin = origin)
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
		elif (destination.is_general_purpose_register64() or destination.is_memory_address64(strict_size = True)) and source.is_none() and immediate.is_none():
			# IMUL r64/m64: REX.W F7 /5
			self.operands = 1
			self.source = destination
			self.size = 1 + 2 + self.source.get_modrm_extra_length()
			self.output_registers_list = [rdx, rax]
			self.input_registers_list = [rax]
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
		elif destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()) and immediate.is_none():
			# IMUL r64, r64/m64: REX.W 0F AF /r
			self.operands = 2
			self.source = source
			self.destination = destination
			self.size = 1 + 3 + source.get_modrm_extra_length()
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
		elif destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()) and immediate.is_int32():
			# IMUL r64, r64/m64,  imm8: REX.W 6B /r ib
			# IMUL r64, r64/m64, imm32: REX.W 69 /r id
			self.operands = 3
			self.source = source
			self.destination = destination
			self.immediate = immediate
			if immediate.is_sint8():
				self.size = 1 + 2 + source.get_modrm_extra_length() + 1
			else:
				self.size = 1 + 2 + source.get_modrm_extra_length() + 4
			self.output_registers_list = destination.get_registers_list()
			self.input_registers_list = source.get_registers_list()
		else:
			raise ValueError('Invalid operands in instruction IMUL {0}, {1}, {2}'.format(destination, source, immediate))

	def __str__(self):
		if self.operands == 1:
			return "IMUL {0}".format(self.source)
		elif self.operands == 2:
			return "IMUL {0}, {1}".format(self.destination, self.source)
		else:
			return "IMUL {0}, {1}, {2}".format(self.destination, self.source, self.immediate)

	def get_input_registers_list(self):
		return self.input_registers_list

	def get_output_registers_list(self):
		return self.output_registers_list

	def get_constant(self):
		if self.operands == 1:
			if self.source.is_constant():
				return self.source.constant
			else:
				return None
		else:
			if self.source.is_constant():
				return self.source.constant
			else:
				return None

	def get_local_variable(self):
		if self.operands == 1:
			if self.destination.is_local_variable():
				return self.destination.variable
			else:
				return None
		else:
			if self.source.is_local_variable():
				return self.source.variable
			else:
				return None

class MulInstruction(Instruction):
	def __init__(self, source, origin = None):
		super(MulInstruction, self).__init__("MUL", origin = origin)
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

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class MoveExtendInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		super(MoveExtendInstruction, self).__init__(name, destination, source, origin = origin)
		allowed_instructions = ['MOVZX', 'MOVSX']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		if destination.is_general_purpose_register64() and (source.is_general_purpose_register8() or source.is_memory_address8(strict_size=True)):
			# MOVZX r64, r8/m8: REX.W 0F B6 /r
			# MOVSX r64, r8/m8: REX.W 0F BE /r
			self.size = 1 + 3 + source.get_modrm_extra_length()
			self.always_has_rex_prefix = True
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register8() or source.is_memory_address8(strict_size=True)):
			# MOVZX r32, r8/m8: 0F B6 /r
			# MOVSX r32, r8/m8: 0F BE /r
			self.size = 3 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register8() or source.is_memory_address8(strict_size=True)):
			# MOVZX r16, r8/m8: 66 0F B6 /r
			# MOVSX r16, r8/m8: 66 0F BE /r
			self.size = 3 + 1 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register64() and (source.is_general_purpose_register16() or source.is_memory_address16(strict_size=True)):
			# MOVZX r64, r16/m16: REX.W 0F B7 /r
			# MOVSX r64, r16/m16: REX.W 0F BF /r
			self.size = 1 + 3 + source.get_modrm_extra_length()
			self.always_has_rex_prefix = True
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register16() or source.is_memory_address16(strict_size=True)):
			# MOVZX r32, r16/m16: 0F B7 /r
			# MOVSX r32, r16/m16: 0F BF /r
			self.size = 3 + source.get_modrm_extra_length()
		elif name == "MOVSX" and destination.is_general_purpose_register64() and (source.is_general_purpose_register32() or source.is_memory_address32(strict_size=True)):
			# MOVSX r64, r32/m32: REX.W 63 /r
			self.size = 1 + 2 + source.get_modrm_extra_length()
			self.always_has_rex_prefix = True
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

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class MovInstruction(BinaryInstruction):
	def __init__(self, destination, source, origin = None):
		super(MovInstruction, self).__init__('MOV', destination, source, origin = origin)
		if destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			# MOV r64, r64/m64: REX.W 8B /r
			self.size = 1 + 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# MOV r32, r32/m32: 8B /r
			self.size = 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()):
			# MOV r16, r16/m16: 66 8B /r
			self.size = 1 + 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register8() and (source.is_general_purpose_register8() or source.is_memory_address8()):
			# MOV r8, r8/m8: 8A /r
			self.size = 2 + source.get_modrm_extra_length()
		elif (destination.is_general_purpose_register64() or destination.is_memory_address64()) and source.is_general_purpose_register64():
			# MOV r64/m64, r64: REX.W 89 /r
			self.size = 1 + 2 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32()) and source.is_general_purpose_register32():
			# MOV r32/m32, r32: 89 /r
			self.size = 2 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16()) and source.is_general_purpose_register16():
			# MOV r16/m16, r16: 66 89 /r
			self.size = 1 + 2 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register8() or destination.is_memory_address8()) and source.is_general_purpose_register8():
			# MOV r8/m8, r8: 88 /r
			self.size = 2 + destination.get_modrm_extra_length()
		elif destination.is_general_purpose_register64() and source.is_int64():
			# MOV r64, imm64: REX.W B8+ rq
			self.size = 1 + 1 + 8
		elif destination.is_general_purpose_register32() and source.is_int32():
			# MOV r32, imm32: B8 +rd id
			self.size = 1 + 4
		elif destination.is_general_purpose_register16() and source.is_int16():
			# MOV r16, imm16: 66 B8 +rw iw
			self.size = 1 + 1 + 2
		elif destination.is_general_purpose_register8() and source.is_int8():
			# MOV r8, imm8: B0 +rb ib
			self.size = 1 + 1
		elif (destination.is_general_purpose_register64() or destination.is_memory_address64(strict_size = True)) and source.is_sint32():
			# MOV r64/m64, imm32: REX.W C7 /0 id
			self.size = 1 + 2 + 4 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register32() or destination.is_memory_address32(strict_size = True)) and source.is_int32():
			# MOV r32/m32, imm32: C7 /0 id
			self.size = 2 + 4 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register16() or destination.is_memory_address16(strict_size = True)) and source.is_int16():
			# MOV r16/m16, imm16: 66 C7 /0 iw
			self.size = 1 + 2 + 2 + destination.get_modrm_extra_length()
		elif (destination.is_general_purpose_register8() or destination.is_memory_address8(strict_size = True)) and source.is_int8():
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

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		elif self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class ByteSwapInstruction(Instruction):
	def __init__(self, destination, origin = None):
		super(ByteSwapInstruction, self).__init__('BSWAP', origin = origin)
		self.destination = destination
		if destination.is_general_purpose_register64():
			# BSWAP r64: REX.W + 0F C8+rd
			self.size = 1 + 2
		elif destination.is_general_purpose_register32():
			# BSWAP r32: 0F C8+rd
			self.size = 2
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format(self.name, destination))

	def __str__(self):
		return "{0} {1}".format(self.name, self.destination)

	def get_input_registers_list(self):
		return [self.destination.register]

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class UnaryBitCountInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'BSF', 'BSR', 'LZCNT', 'TZCNT', 'POPCNT' ]
		if name == 'LZCNT':
			super(UnaryBitCountInstruction, self).__init__(name, isa_extension = 'LZCNT', origin = origin)
		elif name == 'TZCNT':
			super(UnaryBitCountInstruction, self).__init__(name, isa_extension = 'BMI', origin = origin)
		elif name == 'POPCNT':
			super(UnaryBitCountInstruction, self).__init__(name, isa_extension = 'POPCNT', origin = origin)
		elif name in ['BSF', 'BSR']:
			super(UnaryBitCountInstruction, self).__init__(name, origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		self.destination = destination
		self.source = source
		if destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			# BSR    r64, r64/m64: REX.W + 0F BD /r
			# BSF    r64, r64/m64: REX.W + 0F BC /r
			# LZCNT  r64, r64/m64: REX.W + F3 0F BD /r
			# TZCNT  r64, r64/m64: REX.W + F3 0F BC /r
			# POPCNT r64, r64/m64: REX.W + F3 0F B8 /r
			self.size = 1 + 4 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# BSR    r32, r32/m32: 0F BD /r
			# BSF    r32, r32/m32: 0F BC /r
			# LZCNT  r32, r32/m32: F3 0F BD /r
			# TZCNT  r32, r32/m32: F3 0F BC /r
			# POPCNT r32, r32/m32: F3 0F B8 /r
			self.size = 4 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register16() and (source.is_general_purpose_register16() or source.is_memory_address16()):
			# BSR    r16, r16/m16: 66 0F BD /r
			# BSF    r16, r16/m16: 66 0F BC /r
			# LZCNT  r16, r16/m16: 66 F3 0F BD /r
			# TZCNT  r16, r16/m16: 66 F3 0F BC /r
			# POPCNT r16, r16/m16: 66 F3 0F B8 /r
			self.size = 1 + 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class CRC32Instruction(Instruction):
	def __init__(self, destination, source, origin = None):
		super(CRC32Instruction, self).__init__("CRC32", isa_extension = "SSE4.2", origin = origin)
		self.destination = destination
		self.source = source
		if destination.is_general_purpose_register32() and (source.is_general_purpose_register8() or source.is_memory_address8()):
			# CRC32 r32, r8/r8: F2 REX 0F 38 F0 /r
			
			self.size = 1 + 5 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register16() or source.is_memory_address16()):
			# CRC32 r32, r16/m16: 66 F2 0F 38 F1 /r
			
			self.size = 1 + 5 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# CRC32 r32, r32/m32: F2 0F 38 F1 /r
			
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register64() and (source.is_general_purpose_register8() or source.is_memory_address8()):
			# CRC32 r64, r8/r8: F2 REX.W 0F 38 F0 /r
			
			self.size = 1 + 5 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			# CRC32 r64, r64/m64: F2 REX.W 0F 38 F1 /r
			
			self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format("CRC32", destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list() 

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class UnaryBitManipulationInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		bmi_instructions = ('BLSI', 'BLSMSK', 'BLSR')
		if name in bmi_instructions:
			super(UnaryBitManipulationInstruction, self).__init__(name, isa_extension = 'BMI', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(bmi_instructions)))
		self.destination = destination
		self.source = source
		if destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			#   BLSR r64, r64/m64: VEX.NDD.LZ.0F38.W1 F3 /1
			# BLSMSK r64, r64/m64: VEX.NDD.LZ.0F38.W1 F3 /2
			#   BLSI r64, r64/m64: VEX.NDD.LZ.0F38.W1 F3 /3

			self.size = 3 + 2 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			#   BLSR r32, r32/m32: VEX.NDD.LZ.0F38.W0 F3 /1
			# BLSMSK r32, r32/m32: VEX.NDD.LZ.0F38.W0 F3 /2
			#   BLSI r32, r32/m32: VEX.NDD.LZ.0F38.W0 F3 /3

			self.size = 3 + 2 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class BinaryBitManipulationInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		bmi_instructions = ['ANDN', 'BEXTR']
		bmi2_instructions = ['BZHI', 'MULX', 'PDEP', 'PEXT', 'SARX', 'SHRX', 'SHLX']
		allowed_instructions = bmi_instructions + bmi2_instructions
		if name in bmi_instructions:
			super(BinaryBitManipulationInstruction, self).__init__(name, isa_extension = 'BMI', origin = origin)
		elif name in bmi2_instructions:
			super(BinaryBitManipulationInstruction, self).__init__(name, isa_extension = 'BMI2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name in ['BEXTR', 'BZHI', 'SARX', 'SHRX', 'SHLX'] and destination.is_general_purpose_register64() and (source_x.is_general_purpose_register64() or source_x.is_memory_address64()) and source_y.is_general_purpose_register64():
			# BEXTR r64, r64/m64, r64: VEX.NDS.LZ.0F38.W1 F7 /r
			# BZHI  r64, r64/m64, r64: VEX.NDS.LZ.0F38.W1 F5 /r
			# SARX  r64, r64/m64, r64: VEX.NDS.LZ.F3.0F38.W1 F7 /r
			# SHRX  r64, r64/m64, r64: VEX.NDS.LZ.F2.0F38.W1 F7 /r
			# SHLX  r64, r64/m64, r64: VEX.NDS.LZ.66.0F38.W1 F7 /r

			self.size = 3 + 2 + source_x.get_modrm_extra_length()
		elif name in ['BEXTR', 'BZHI', 'SARX', 'SHRX', 'SHLX'] and destination.is_general_purpose_register32() and (source_x.is_general_purpose_register32() or source_x.is_memory_address32()) and source_y.is_general_purpose_register32():
			# BEXTR r32, r32/m32, r32: VEX.NDS.LZ.0F38.W0 F7 /r
			# BZHI  r32, r32/m32, r32: VEX.NDS.LZ.0F38.W0 F5 /r
			# SARX  r32, r32/m32, r32: VEX.NDS.LZ.F3.0F38.W0 F7 /r
			# SHRX  r32, r32/m32, r32: VEX.NDS.LZ.F2.0F38.W0 F7 /r
			# SHLX  r32, r32/m32, r32: VEX.NDS.LZ.66.0F38.W0 F7 /r

			self.size = 3 + 2 + source_x.get_modrm_extra_length()
		elif name in ['ANDN', 'MULX', 'PDEP', 'PEXT'] and destination.is_general_purpose_register64() and source_x.is_general_purpose_register64() and (source_y.is_general_purpose_register64()  or source_y.is_memory_address64()):
			# ANDN r64, r64, r64/m64: VEX.NDS.LZ.0F38.W1 F2 /r
			# MULX r64, r64, r64/m64: VEX.NDS.LZ.0F38.W1 F6 /r
			# PDEP r64, r64, r64/m64: VEX.NDS.LZ.F2.0F38.W1 F5 /r
			# PEXT r64, r64, r64/m64: VEX.NDS.LZ.F3.0F38.W1 F5 /r
			
			self.size = 3 + 2 + source_x.get_modrm_extra_length()
		elif name in ['ANDN', 'MULX', 'PDEP', 'PEXT'] and destination.is_general_purpose_register32() and source_x.is_general_purpose_register32() and (source_y.is_general_purpose_register32() or source_y.is_memory_address32()):
			# ANDN r32, r32, r32/m32: VEX.NDS.LZ.0F38.W0 F2 /r
			# MULX r32, r32, r32/m32: VEX.NDS.LZ.0F38.W0 F6 /r
			# PDEP r32, r32, r32/m32: VEX.NDS.LZ.F2.0F38.W0 F5 /r
			# PEXT r32, r32, r32/m32: VEX.NDS.LZ.F3.0F38.W0 F5 /r
			
			self.size = 3 + 2 + source_x.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_x.is_constant():
			return self.source_x.constant
		elif self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_x.is_local_variable():
			return self.source_x.variable
		elif self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class BmiRotateInstruction(Instruction):
	def __init__(self, destination, source, immediate, origin = None):
		super(BmiRotateInstruction, self).__init__('RORX', isa_extension = 'BMI2', origin = origin)
		self.destination = destination
		self.source = source
		self.immediate = immediate
		if destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()) and immediate.is_int8():
			# RORX r64, r64/m64, imm8: VEX.LZ.F2.0F3A.W1.F0 /r ib

			self.size = 3 + 1 + source.get_modrm_extra_length() + 1
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()) and immediate.is_int8():
			# RORX r32, r32/m32, imm8: VEX.LZ.F2.0F3A.W0.F0 /r ib

			self.size = 3 + 1 + source.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction RORX {0}, {1}, {2}'.format(destination, source, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.immediate)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class ConditionalJumpInstruction(Instruction):
	def __init__(self, name, destination, origin = None):
		super(ConditionalJumpInstruction, self).__init__(name, origin = origin)
		allowed_instructions = [ 'JA',  'JAE',  'JB',  'JBE',  'JC',  'JE',  'JG',  'JGE',  'JL',  'JLE',  'JO',  'JP',  'JPO',  'JS',  'JZ',
								'JNA', 'JNAE', 'JNB', 'JNBE', 'JNC', 'JNE', 'JNG', 'JNGE', 'JNL', 'JNLE', 'JNO', 'JNP', 'JNPO', 'JNS', 'JNZ']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
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

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class CompareAndBranchInstruction(Instruction):
	def __init__(self, compare, branch, origin = None):
		super(CompareAndBranchInstruction, self).__init__('CMP.%s' % branch.name, origin = origin)
		self.compare = compare
		self.branch = branch
	
	def __str__(self):
		return "{0} {1}, {2}, .{3}".format(self.name, self.compare.source, self.compare.destination, self.branch.destination)

	def get_input_registers_list(self):
		return self.compare.get_input_register_list()

	def get_output_registers_list(self):
		return self.compare.get_output_registers_list()

	def get_constant(self):
		return self.compare.get_constant()

	def get_local_variable(self):
		return self.compare.get_local_variable()

class CmovInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		super(CmovInstruction, self).__init__(name,  destination, source, isa_extension = 'CMOV', origin = origin)
		allowed_instructions = [ 'CMOVA',  'CMOVAE',  'CMOVB',  'CMOVBE',  'CMOVC',  'CMOVE',  'CMOVG',  'CMOVGE',  'CMOVL',  'CMOVLE',  'CMOVO',  'CMOVP',  'CMOVPO',  'CMOVS',  'CMOVZ',
								'CMOVNA', 'CMOVNAE', 'CMOVNB', 'CMOVNBE', 'CMOVNC', 'CMOVNE', 'CMOVNG', 'CMOVNGE', 'CMOVNL', 'CMOVNLE', 'CMOVNO', 'CMOVNP', 'CMOVNPO', 'CMOVNS', 'CMOVNZ']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_general_purpose_register64() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			#   CMOVA r64, r64/m64: REX.W + 0F 47 /r
			#  CMOVAE r64, r64/m64: REX.W + 0F 43 /r
			#   CMOVB r64, r64/m64: REX.W + 0F 42 /r
			#  CMOVBE r64, r64/m64: REX.W + 0F 46 /r
			#   CMOVC r64, r64/m64: REX.W + 0F 42 /r
			#   CMOVE r64, r64/m64: REX.W + 0F 44 /r
			#   CMOVG r64, r64/m64: REX.W + 0F 4F /r
			#  CMOVGE r64, r64/m64: REX.W + 0F 4D /r
			#   CMOVL r64, r64/m64: REX.W + 0F 4C /r
			#  CMOVLE r64, r64/m64: REX.W + 0F 4E /r
			#  CMOVNA r64, r64/m64: REX.W + 0F 46 /r
			# CMOVNAE r64, r64/m64: REX.W + 0F 42 /r
			#  CMOVNB r64, r64/m64: REX.W + 0F 43 /r
			# CMOVNBE r64, r64/m64: REX.W + 0F 47 /r
			#  CMOVNC r64, r64/m64: REX.W + 0F 43 /r
			#  CMOVNE r64, r64/m64: REX.W + 0F 45 /r
			#  CMOVNG r64, r64/m64: REX.W + 0F 4E /r
			# CMOVNGE r64, r64/m64: REX.W + 0F 4C /r
			#  CMOVNL r64, r64/m64: REX.W + 0F 4D /r
			# CMOVNLE r64, r64/m64: REX.W + 0F 4F /r
			#  CMOVNO r64, r64/m64: REX.W + 0F 41 /r
			#  CMOVNP r64, r64/m64: REX.W + 0F 4B /r
			#  CMOVNS r64, r64/m64: REX.W + 0F 49 /r
			#  CMOVNZ r64, r64/m64: REX.W + 0F 45 /r
			#   CMOVO r64, r64/m64: REX.W + 0F 40 /r
			#   CMOVP r64, r64/m64: REX.W + 0F 4A /r
			#  CMOVPE r64, r64/m64: REX.W + 0F 4A /r
			#  CMOVPO r64, r64/m64: REX.W + 0F 4B /r
			#   CMOVS r64, r64/m64: REX.W + 0F 48 /r
			#   CMOVZ r64, r64/m64: REX.W + 0F 44 /r
			self.destination = destination
			self.source = source
			self.size = 1 + 3 + source.get_modrm_extra_length()
		elif destination.is_general_purpose_register32() and (source.is_general_purpose_register32() or source.is_memory_address32()):
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
		return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SetInstruction(Instruction):
	def __init__(self, name, destination, origin = None):
		super(SetInstruction, self).__init__(name, origin = origin)
		allowed_instructions = [ 'SETA',  'SETAE',  'SETB',  'SETBE',  'SETC',  'SETE',  'SETG',  'SETGE',  'SETL',  'SETLE',  'SETO',  'SETP',  'SETPO',  'SETS',  'SETZ',
								'SETNA', 'SETNAE', 'SETNB', 'SETNBE', 'SETNC', 'SETNE', 'SETNG', 'SETNGE', 'SETNL', 'SETNLE', 'SETNO', 'SETNP', 'SETNPO', 'SETNS', 'SETNZ']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_general_purpose_register8() or destination.is_memory_address8():
			#   SETA r8/m8: 0F 97 /r
			#  SETAE r8/m8: 0F 93 /r
			#   SETB r8/m8: 0F 92 /r
			#  SETBE r8/m8: 0F 96 /r
			#   SETC r8/m8: 0F 92 /r
			#   SETE r8/m8: 0F 94 /r
			#   SETG r8/m8: 0F 9F /r
			#  SETGE r8/m8: 0F 9D /r
			#   SETL r8/m8: 0F 9C /r
			#  SETLE r8/m8: 0F 9E /r
			#  SETNA r8/m8: 0F 96 /r
			# SETNAE r8/m8: 0F 92 /r
			#  SETNB r8/m8: 0F 93 /r
			# SETNBE r8/m8: 0F 97 /r
			#  SETNC r8/m8: 0F 93 /r
			#  SETNE r8/m8: 0F 95 /r
			#  SETNG r8/m8: 0F 9E /r
			# SETNGE r8/m8: 0F 9C /r
			#  SETNL r8/m8: 0F 9D /r
			# SETNLE r8/m8: 0F 9F /r
			#  SETNO r8/m8: 0F 91 /r
			#  SETNP r8/m8: 0F 9B /r
			#  SETNS r8/m8: 0F 99 /r
			#  SETNZ r8/m8: 0F 95 /r
			#   SETO r8/m8: 0F 90 /r
			#   SETP r8/m8: 0F 9A /r
			#  SETPE r8/m8: 0F 9A /r
			#  SETPO r8/m8: 0F 9B /r
			#   SETS r8/m8: 0F 98 /r
			#   SETZ r8/m8: 0F 94 /r
			self.destination = destination
			self.size = 3 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}}'.format(name, destination))

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

	def get_constant(self):
		return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class MmxClearStateInstruction(Instruction):
	def __init__(self, name, origin = None):
		allowed_instructions = ( 'EMMS', 'FEMMS' )
		if name == 'EMMS':
			# EMMS: 0F 77
			
			super(MmxClearStateInstruction, self).__init__(name, isa_extension = 'MMX', origin = origin)
			self.size = 2
		elif name == 'FEMMS':
			# FEMMS: 0F 0E

			super(MmxClearStateInstruction, self).__init__(name, isa_extension = '3dnow!', origin = origin)
			self.size = 2
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(('EMMS', 'FEMMS')))

	def __str__(self):
		return self.name

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return list()

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class AvxZeroInstruction(Instruction):
	def __init__(self, name, origin = None):
		allowed_instructions = [ 'VZEROALL', 'VZEROUPPER' ]
		if name in allowed_instructions:
			super(AvxZeroInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			# VZEROUPPER: VEX.128.0F.WIG 77
			#   VZEROALL: VEX.256.0F.WIG 77

			self.size = 2 + 1
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))

	def __str__(self):
		return self.name

	def get_input_registers_list(self):
		if self.name == 'VZEROALL':
			return []
		else:
			return [ymm0, ymm1, ymm2, ymm3, ymm4,
			        ymm5, ymm6, ymm7, ymm8, ymm9,
			        ymm10, ymm11, ymm12, ymm13, ymm14, ymm15]

	def get_output_registers_list(self):
		return [ymm0, ymm1, ymm2, ymm3, ymm4,
		        ymm5, ymm6, ymm7, ymm8, ymm9,
		        ymm10, ymm11, ymm12, ymm13, ymm14, ymm15]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class SseMovInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		sse_instructions = ['MOVAPS', 'MOVUPS', 'MOVNTPS']
		sse2_instructions = ['MOVAPD', 'MOVUPD', 'MOVNTPD', 'MOVDQA', 'MOVDQU', 'MOVNTDQ']
		sse3_instructions = ['LDDQU']
		sse41_instructions = ['MOVNTDQA']
		load_instructions = ['LDDQU', 'MOVNTDQA']
		store_instructions = ['MOVNTPS', 'MOVNTPD', 'MOVNTDQ']
		mov_instructions = ['MOVAPS', 'MOVUPS', 'MOVAPD', 'MOVUPD', 'MOVDQA', 'MOVDQU']
		allowed_instructions = sse_instructions + sse2_instructions + sse3_instructions + sse41_instructions
		if name in sse_instructions:
			super(SseMovInstruction, self).__init__(name, destination, source, isa_extension = 'SSE', origin = origin)
		elif name in sse2_instructions:
			super(SseMovInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
		elif name in sse3_instructions:
			super(SseMovInstruction, self).__init__(name, destination, source, isa_extension = 'SSE3', origin = origin)
		elif name in sse41_instructions:
			super(SseMovInstruction, self).__init__(name, destination, source, isa_extension = 'SSE4.1', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name in load_instructions and destination.is_sse_register() and source.is_memory_address128():
			#    LDDQU xmm, m128: F2 0F F0 /r
			# MOVNTDQA xmm, m128: 66 0F 38 2A /r
			if name == 'LDDQU': 
				self.size = 4 + source.get_modrm_extra_length()
			else:
				self.size = 1 + 4 + source.get_modrm_extra_length()
		elif name in store_instructions and destination.is_memory_address128() and source.is_sse_register():
			# MOVNTPS m128, xmm: 0F 2B /r
			# MOVNTPD m128, xmm: 66 0F 2B /r
			# MOVNTDQ m128, xmm: 66 0F E7 /r
			if name in sse_instructions:
				self.size = 3 + source.get_modrm_extra_length()
			else:
				self.size = 1 + 3 + source.get_modrm_extra_length()
		elif name in mov_instructions and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# MOVAPS xmm, xmm/m128: 0F 28 /r
			# MOVUPS xmm, xmm/m128: 0F 10 /r
			# MOVAPD xmm, xmm/m128: 66 0F 28 /r
			# MOVUPD xmm, xmm/m128: 66 0F 10 /r
			# MOVDQA xmm, xmm/m128: 66 0F 6F /r
			# MOVDQU xmm, xmm/m128: F3 0F 6F /r
			if name in sse_instructions:
				self.size = 3 + source.get_modrm_extra_length()
			else:
				self.size = 1 + 3 + source.get_modrm_extra_length()
		elif name in mov_instructions and (destination.is_sse_register() or destination.is_memory_address128()) and source.is_sse_register():
			# MOVAPS xmm/m128, xmm: 0F 29 /r
			# MOVUPS xmm/m128, xmm: 0F 11 /r
			# MOVAPD xmm/m128, xmm: 66 0F 29 /r
			# MOVUPD xmm/m128, xmm: 66 0F 11 /r
			# MOVDQA xmm/m128, xmm: 66 0F 7F /r
			# MOVDQU xmm/m128, xmm: F3 0F 7F /r
			if name in sse_instructions:
				self.size = 3 + destination.get_modrm_extra_length()
			else:
				self.size = 1 + 3 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		input_registers_list = self.source.get_registers_list()
		if self.destination.is_memory_address():
			input_registers_list += self.destination.get_registers_list()
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_sse_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		elif self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxMovInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'VMOVAPS', 'VMOVUPS', 'VMOVAPD', 'VMOVUPD', 'VMOVDQA', 'VMOVDQU' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		super(AvxMovInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		self.destination = destination
		self.source = source
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# VMOVAPS xmm, xmm/m128: VEX.128.0F.WIG 28 /r
			# VMOVUPS xmm, xmm/m128: VEX.128.0F.WIG 10 /r
			# VMOVAPD xmm, xmm/m128: VEX.128.66.0F.WIG 28 /r
			# VMOVUPD xmm, xmm/m128: VEX.128.66.0F.WIG 10 /r
			# VMOVDQA xmm, xmm/m128: VEX.128.66.0F.WIG 6F /r
			# VMOVDQU xmm, xmm/m128: VEX.128.F3.0F.WIG 6F /r
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		elif destination.is_avx_register() and (source.is_avx_register() or source.is_memory_address256()):
			# VMOVAPS ymm, ymm/m256: VEX.256.0F.WIG 28 /r
			# VMOVUPS ymm, ymm/m256: VEX.256.0F.WIG 10 /r
			# VMOVAPD ymm, ymm/m256: VEX.256.66.0F.WIG 28 /r
			# VMOVUPD ymm, ymm/m256: VEX.256.66.0F.WIG 10 /r
			# VMOVDQA ymm, ymm/m256: VEX.256.66.0F.WIG 6F /r
			# VMOVDQU ymm, ymm/m256: VEX.256.F3.0F.WIG 6F /r
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		elif (destination.is_sse_register() or destination.is_memory_address128()) and source.is_sse_register():
			# VMOVAPS xmm/m128, xmm: VEX.128.0F.WIG 29 /r
			# VMOVUPS xmm/m128, xmm: VEX.128.0F.WIG 11 /r
			# VMOVAPD xmm/m128, xmm: VEX.128.66.0F.WIG 29 /r
			# VMOVUPD xmm/m128, xmm: VEX.128.66.0F.WIG 11 /r
			# VMOVDQA xmm/m128, xmm: VEX.128.66.0F.WIG 7F /r
			# VMOVDQU xmm/m128, xmm: VEX.128.F3.0F.WIG 7F /r
			self.size = destination.get_vex_extra_length() + 1 + destination.get_modrm_extra_length()
		elif (destination.is_avx_register() or destination.is_memory_address256()) and source.is_avx_register():
			# VMOVAPS ymm/m256, ymm: VEX.256.0F.WIG 29 /r
			# VMOVUPS ymm/m256, ymm: VEX.256.0F.WIG 11 /r
			# VMOVAPD ymm/m256, ymm: VEX.256.66.0F.WIG 29 /r
			# VMOVUPD ymm/m256, ymm: VEX.256.66.0F.WIG 11 /r
			# VMOVDQA ymm/m256, ymm: VEX.256.66.0F.WIG 7F /r
			# VMOVDQU ymm/m256, ymm: VEX.256.F3.0F.WIG 7F /r
			self.size = destination.get_vex_extra_length() + 1 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		input_registers_list = self.source.get_registers_list()
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		elif self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseCrossMovHalfInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = ['MOVLHPS', 'MOVHLPS']
		if name in allowed_instructions:
			super(SseCrossMovHalfInstruction, self).__init__(name, isa_extension = 'SSE', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source.is_sse_register():
			# MOVLHPS xmm, xmm: 0F 16 /r
			# MOVHLPS xmm, xmm: 0F 12 /r

			self.source = source
			self.destination = destination
			self.size = 3
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class AvxCrossMovHalfInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VMOVLHPS', 'VMOVHLPS']
		if name in allowed_instructions:
			super(AvxCrossMovHalfInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register():
			# VMOVLHPS xmm, xmm, xmm: VEX.NDS.128.0F.WIG 16 /r
			# VMOVHLPS xmm, xmm, xmm: VEX.NDS.128.0F.WIG 12 /r

			self.source_x = source_x
			self.source_y = source_y
			self.destination = destination
			self.size = 4
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class SseMovHalfInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		sse_instructions = ['MOVLPS', 'MOVHPS']
		sse2_instructions = ['MOVLPD', 'MOVHPD']
		allowed_instructions = sse_instructions + sse2_instructions
		if name in sse_instructions:
			super(SseMovHalfInstruction, self).__init__(name, isa_extension = 'SSE', origin = origin)
		elif name in sse2_instructions:
			super(SseMovHalfInstruction, self).__init__(name, isa_extension = 'SSE2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		self.source = source
		self.destination = destination
		if destination.is_sse_register() and source.is_memory_address64():
			# MOVLPS xmm, m64: 0F 12 /r
			# MOVHPS xmm, m64: 0F 16 /r
			# MOVLPD xmm, m64: 66 0F 12 /r
			# MOVHPD xmm, m64: 66 0F 16 /r

			if name in sse_instructions:
				self.size = 3 + source.get_modrm_extra_length()
			else:
				self.size = 4 + source.get_modrm_extra_length()
		elif destination.is_memory_address64() and source.is_sse_register():
			# MOVLPS m64, xmm: 0F 13 /r
			# MOVHPS m64, xmm: 0F 17 /r
			# MOVLPD m64, xmm: 66 0F 13 /r
			# MOVHPD m64, xmm: 66 0F 17 /r

			if name in sse_instructions:
				self.size = 3 + destination.get_modrm_extra_length()
			else:
				self.size = 4 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		elif self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class AvxMovHalfInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = ['VMOVLPS', 'VMOVHPS', 'VMOVLPD', 'VMOVHPD']
		if name in allowed_instructions:
			super(AvxMovHalfInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		self.source_x = source_x
		self.source_y = source_y
		self.destination = destination
		if destination.is_sse_register() and source_x.is_sse_register() and source_y.is_memory_address64():
			# VMOVLPS xmm, xmm, m64: VEX.NDS.128.0F.WIG 12 /r
			# VMOVHPS xmm, xmm, m64: VEX.NDS.128.0F.WIG 16 /r
			# VMOVLPD xmm, xmm, m64: VEX.NDS.128.66.0F.WIG 12 /r
			# VMOVHPD xmm, xmm, m64: VEX.NDS.128.66.0F.WIG 16 /r

			self.size = 5 + source_y.get_modrm_extra_length()
		elif destination.is_sse_register() and source_x.is_memory_address64() and source_y.is_none():
			# VMOVLPS xmm, xmm, m64: VEX.NDS.128.0F.WIG 12 /r
			# VMOVHPS xmm, xmm, m64: VEX.NDS.128.0F.WIG 16 /r
			# VMOVLPD xmm, xmm, m64: VEX.NDS.128.66.0F.WIG 12 /r
			# VMOVHPD xmm, xmm, m64: VEX.NDS.128.66.0F.WIG 16 /r

			self.source_x = destination
			self.source_y = source_x
			self.size = 5 + source_x.get_modrm_extra_length()
		elif destination.is_memory_address64() and source_x.is_sse_register() and source_y.is_none():
			# MOVLPS m64, xmm: VEX.NDS.128.0F.WIG 13 /r
			# MOVHPS m64, xmm: VEX.NDS.128.0F.WIG 17 /r
			# MOVLPD m64, xmm: VEX.NDS.128.66.0F.WIG 13 /r
			# MOVHPD m64, xmm: VEX.NDS.128.66.0F.WIG 17 /r

			self.size = 5 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source_x, source_y))

	def __str__(self):
		if self.source_y.is_none():
			return "{0} {1}, {2}".format(self.name, self.destination, self.source_x)
		else:
			return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		input_registers_list = self.source_x.get_registers_list() + self.source_y.get_registers_list()
		if self.destination.is_memory_address():
			input_registers_list += self.destination.get_registers_list()
		return input_registers_list 

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		elif self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class MmxSseMovWordInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'MOVD', 'MOVQ' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name == 'MOVD' and destination.is_mmx_register() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# MOVD mm, r32/m32: 0F 6E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'MMX', origin = origin)
			self.size = 3 + source.get_modrm_extra_length()
		elif name == 'MOVQ' and destination.is_mmx_register() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			# MOVQ mm, r64/m64: REX.W 0F 6E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'MMX', origin = origin)
			self.size = 1 + 3 + source.get_modrm_extra_length()
		elif name == 'MOVD' and (destination.is_general_purpose_register32() or destination.is_memory_address32()) or source.is_mmx_register():
			# MOVD r32/m32, mm: 0F 7E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'MMX', origin = origin)
			self.size = 3 + destination.get_modrm_extra_length()
		elif name == 'MOVQ' and (destination.is_general_purpose_register64() or destination.is_memory_address64()) or source.is_mmx_register():
			# MOVQ r64/m64, mm: REX.W 0F 7E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'MMX', origin = origin)
			self.size = 1 + 3 + destination.get_modrm_extra_length()
		elif name == 'MOVD' and destination.is_sse_register() and (source.is_general_purpose_register32() or source.is_memory_address32()):
			# MOVD xmm, r32/m32: 66 0F 6E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
			self.size = 1 + 3 + source.get_modrm_extra_length()
		elif name == 'MOVQ' and destination.is_sse_register() and (source.is_general_purpose_register64() or source.is_memory_address64()):
			# MOVQ xmm, r64/m64: 66 REX.W 0F 6E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
			self.size = 1 + 1 + 3 + source.get_modrm_extra_length()
		elif name == 'MOVD' and (destination.is_general_purpose_register32() or destination.is_memory_address32()) or source.is_sse_register():
			# MOVD r32/m32, xmm: 66 0F 7E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
			self.size = 1 + 3 + destination.get_modrm_extra_length()
		elif name == 'MOVQ' and (destination.is_general_purpose_register64() or destination.is_memory_address64()) or source.is_sse_register():
			# MOVQ r64/m64, xmm: 66 REX.W 0F 7E /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
			self.size = 1 + 1 + 3 + destination.get_modrm_extra_length()
		elif name == 'MOVQ' and destination.is_mmx_register() and (source.is_mmx_register() or source.is_memory_address64()):
			# MOVQ mm, mm/m64: 0F 6F /r
			
			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'MMX', origin = origin)
			self.size = 3 + source.get_modrm_extra_length()
		elif name == 'MOVQ' and (destination.is_mmx_register() or destination.is_memory_address64()) and source.is_mmx_register():
			# MOVQ mm/m64, mm: 0F 7F /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'MMX', origin = origin)
			self.size = 3 + destination.get_modrm_extra_length()
		elif name == 'MOVQ' and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()):
			# MOVQ xmm, xmm/m64: F3 0F 7E /r
			
			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
			self.size = 3 + source.get_modrm_extra_length()
		elif name == 'MOVQ' and (destination.is_sse_register() or destination.is_memory_address64()) and source.is_sse_register():
			# MOVQ xmm/m64, xmm: 66 0F D6 /r

			super(MmxSseMovWordInstruction, self).__init__(name, destination, source, isa_extension = 'SSE2', origin = origin)
			self.size = 3 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		input_registers_list = self.source.get_registers_list()
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		elif self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class MxcsrControlInstruction(Instruction):
	def __init__(self, name, operand, origin = None):
		allowed_instructions = ['LDMXCSR', 'STMXCSR']
		if name in allowed_instructions:
			super(MxcsrControlInstruction, self).__init__(name, isa_extension = 'SSE', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if operand.is_memory_address32():
			# LDMXCSR m32: 0F AE /2
			# STMXCSR m32: 0F AE /3
			self.operand = operand
			self.size = 3 + operand.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format(name, operand))

	def __str__(self):
		return "{0} {1}".format(self.name, self.operand)

	def get_input_registers_list(self):
		return self.operand.get_registers_list()

	def get_output_registers_list(self):
		return list()

	def get_constant(self):
		if self.name == 'LDMXCSR' and self.operand.is_constant():
			return self.operand.constant
		else:
			return None

	def get_local_variable(self):
		if self.operand.is_local_variable():
			return self.operand.variable
		else:
			return None

class AvxExtract128Instruction(Instruction):
	def __init__(self, name, destination, source, immediate, origin = None):
		if name == 'VEXTRACTF128':
			super(AvxExtract128Instruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		elif name == 'VEXTRACTI128':
			super(AvxExtract128Instruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(['VEXTRACTF128', 'VEXTRACTI128'])))
		self.destination = destination
		self.source = source
		self.immediate = immediate
		if (destination.is_sse_register() or destination.is_memory_address128()) and source.is_avx_register() and immediate.is_uint8():
			# VEXTRACTF128 xmm/m128, ymm, imm8: VEX.256.66.0F3A.W0 19 /r ib
			# VEXTRACTI128 xmm/m128, ymm, imm8: VEX.256.66.0F3A.W0 39 /r ib

			self.size = 3 + 1 + destination.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.immediate)

	def get_input_registers_list(self):
		input_registers_list = self.source.get_registers_list()
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		return None

	def get_local_variable(self):
		if self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class AvxInsert128Instruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, immediate, origin = None):
		if name == 'VINSERTF128':
			super(AvxInsert128Instruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		elif name == 'VINSERTI128':
			super(AvxInsert128Instruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(['VINSERTF128', 'VINSERTI128'])))
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		self.immediate = immediate
		if destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_sse_register() or source_y.is_memory_address128()) and immediate.is_uint8():
			# VINSERTF128 ymm, ymm, xmm/m128, imm8: VEX.NDS.256.66.0F3A.W0 18 /r ib
			# VINSERTI128 ymm, ymm, xmm/m128, imm8: VEX.NDS.256.66.0F3A.W0 38 /r ib

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}'.format(name, destination, source_x, source_y, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}".format(self.name, self.destination, self.source_x, self.source_y, self.immediate)

	def get_input_registers_list(self):
		input_registers_list = self.source_x.get_registers_list() + self.source_y.get_registers_list()
		return input_registers_list

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxPermute128Instruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, immediate, origin = None):
		if name == 'VPERM2F128':
			super(AvxPermute128Instruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		elif name == 'VPERM2I128':
			super(AvxPermute128Instruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(['VPERM2F128', 'VPERM2I128'])))
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		self.immediate = immediate
		if destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) or immediate.is_uint8():
			# VPERM2F128 ymm, ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.W0 06 /r ib
			# VPERM2I128 ymm, ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.W0 46 /r ib

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}'.format(name, destination, source_x, source_y, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}".format(self.name, self.destination, self.source_x, self.source_y, self.immediate)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxPermuteInstruction(Instruction):
	def __init__(self, name, destination, source, permutation, origin = None):
		allowed_instructions = [ 'VPERMILPS', 'VPERMILPD' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		super(AvxPermuteInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		self.destination = destination
		self.source = source
		self.permutation = permutation
		if destination.is_sse_register() and source.is_sse_register() and (permutation.is_sse_register() or permutation.is_memory_address128()):
			# VPERMILPS xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.W0 0C /r

			self.size = 3 + 1 + permutation.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()) and permutation.is_uint8():
			# VPERMILPS xmm, xmm/m128, imm8: VEX.NDS.128.66.0F3A.W0 04 /r ib
			
			self.size = 3 + 1 + source.get_modrm_extra_length() + 1
		elif destination.is_avx_register() and source.is_avx_register() and (permutation.is_avx_register() or permutation.is_memory_address256()):
			# VPERMILPS ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W0 0C /r

			self.size = 3 + 1 + permutation.get_modrm_extra_length()
		elif destination.is_avx_register() and (source.is_avx_register() or source.is_memory_address256()) and permutation.is_uint8():
			# VPERMILPS ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.W0 04 /r ib
			
			self.size = 3 + 1 + source.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source, permutation))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.permutation)

	def get_input_registers_list(self):
		return self.source.get_registers_list() + self.permutation.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		elif self.permutation.is_constant():
			return self.permutation.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		elif self.permutation.is_local_variable():
			return self.permutation.variable
		else:
			return None

class AvxCrossLanePermuteInstruction(Instruction):
	def __init__(self, name, destination, source, permutation, origin = None):
		allowed_instructions = [ 'VPERMPS', 'VPERMPD', 'VPERMD', 'VPERMQ' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		super(AvxCrossLanePermuteInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
		self.destination = destination
		self.source = source
		self.permutation = permutation
		if name in ('VPERMPS', 'VPERMD') and destination.is_avx_register() and source.is_avx_register() and (permutation.is_avx_register() or permutation.is_memory_address256()):
			# VPERMPS ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W0 16 /r
			#  VPERMD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W0 36 /r

			self.size = 3 + 1 + permutation.get_modrm_extra_length()
		elif name in ('VPERMPD', 'VPERMQ') and destination.is_avx_register() and (source.is_avx_register() or source.is_memory_address256()) and permutation.is_uint8():
			# VPERMPD ymm, ymm/m256, imm8: VEX.NDS.256.66.0F38.W0 01 /r
			#  VPERMQ ymm, ymm/m256, imm8: VEX.NDS.256.66.0F38.W0 00 /r

			self.size = 3 + 1 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source, permutation))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.permutation)

	def get_input_registers_list(self):
		return self.source.get_registers_list() + self.permutation.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		elif self.permutation.is_constant():
			return self.permutation.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		elif self.permutation.is_local_variable():
			return self.permutation.variable
		else:
			return None

class XopPermuteInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, permutation, immediate, origin = None):
		allowed_instructions = [ 'VPERMIL2PS', 'VPERMIL2PD' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		super(XopPermuteInstruction, self).__init__(name, isa_extension = 'XOP', origin = origin)
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		self.permutation = permutation
		self.immediate = immediate
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()) and permutation.is_sse_register() and immediate.is_uint8():

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register() and (permutation.is_sse_register() or permutation.is_memory_address128()) and immediate.is_uint8():

			self.size = 3 + 1 + permutation.get_modrm_extra_length() + 1
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) and permutation.is_avx_register() and immediate.is_uint8():

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and source_y.is_avx_register() and (permutation.is_avx_register() or permutation.is_memory_address256()) and immediate.is_uint8():

			self.size = 3 + 1 + permutation.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}, {5}'.format(name, destination, source_x, source_y, permutation, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}, {5}".format(self.name, self.destination, self.source_x, self.source_y, self.permutation, self.immediate)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list() + self.permutation.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		elif self.permutation.is_constant():
			return self.permutation.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		elif self.permutation.is_local_variable():
			return self.permutation.variable
		else:
			return None

class SseScalarFloatingPointMovInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'MOVSS', 'MOVSD' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name == 'MOVSS':
			super(SseScalarFloatingPointMovInstruction, self).__init__(name, destination, source, 'SSE', origin = origin)
		else:
			super(SseScalarFloatingPointMovInstruction, self).__init__(name, destination, source, 'SSE2', origin = origin)
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
		if self.source.is_memory_address():
			# MOVSx xmm, [mem]
			return self.source.get_registers_list()
		else:
			# MOVSx xmm, xmm or MOVSx [mem], xmm
			return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.destination.is_sse_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		elif self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class AvxScalarFloatingPointMovInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = [ 'VMOVSS', 'VMOVSD' ]
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(allowed_instructions))
		super(AvxScalarFloatingPointMovInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name == 'VMOVSS' and destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register():
			# VMOVSS xmm, xmm, xmm: VEX.NDS.LIG.F3.0F.WIG 10 /r
			# VMOVSS xmm, xmm, xmm: VEX.NDS.LIG.F3.0F.WIG 11 /r

			self.size = destination.get_vex_extra_length() + 1 + destination.get_modrm_extra_length()
		elif name == 'VMOVSS' and destination.is_sse_register() and source_x.is_memory_address32() and source_y.is_none():
			# VMOVSS xmm, m32: VEX.LIG.F3.0F.WIG 10 /r

			self.size = source_x.get_vex_extra_length() + 1 + source_x.get_modrm_extra_length()
		elif name == 'VMOVSS' and destination.is_memory_address32() and source_x.is_sse_register() and source_y.is_none():
			# VMOVSS m32, xmm: VEX.LIG.F3.0F.WIG 11 /r

			self.size = destination.get_vex_extra_length() + 1 + destination.get_modrm_extra_length()
		elif name == 'VMOVSD' and destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register():
			# VMOVSD xmm, xmm, xmm: VEX.NDS.LIG.F2.0F.WIG 10 /r
			# VMOVSD xmm, xmm, xmm: VEX.NDS.LIG.F2.0F.WIG 11 /r

			self.size = destination.get_vex_extra_length() + 1 + destination.get_modrm_extra_length()
		elif name == 'VMOVSD' and destination.is_sse_register() and source_x.is_memory_address64() and source_y.is_none():
			# VMOVSD xmm, m64: VEX.LIG.F2.0F.WIG 10 /r

			self.size = source_x.get_vex_extra_length() + 1 + source_x.get_modrm_extra_length()
		elif name == 'VMOVSD' and destination.is_memory_address64() and source_x.is_sse_register() and source_y.is_none():
			# VMOVSD m64, xmm: VEX.LIG.F2.0F.WIG 11 /r

			self.size = destination.get_vex_extra_length() + 1 + destination.get_modrm_extra_length()
		else:
			if source_y.is_none():
				raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source_x))
			else:
				raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		if self.source_y.is_none():
			return "{0} {1}, {2}".format(self.name, self.destination, self.source_x)
		else:
			return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		input_registers_list = self.source_x.get_registers_list()
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		if self.source_y.is_sse_register():
			input_registers_list.extend(self.source_y.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		if self.destination.is_register():
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source_x.is_constant():
			return self.source_x.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_x.is_local_variable():
			return self.source_x.variable
		elif self.destination.is_local_variable():
			return self.destination.variable
		else:
			return None

class SseFloatingPointBinaryInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
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
			super(SseFloatingPointBinaryInstruction, self).__init__(name, isa_extension = 'SSE', origin = origin)
		elif name in sse2_instructions:
			super(SseFloatingPointBinaryInstruction, self).__init__(name, isa_extension = 'SSE2', origin = origin)
		elif name in sse3_vector_instructions:
			super(SseFloatingPointBinaryInstruction, self).__init__(name, isa_extension = 'SSE3', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(sse_instructions + sse2_instructions))
		self.destination = destination
		self.source = source
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

		if self.name in ['XORPS', 'XORPD', 'ANDNPS', 'ANDNPD'] and self.source == self.destination:
			self.source = self.destination

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		if self.name in ['XORPS', 'XORPD', 'ANDNPS', 'ANDNPD'] and self.source == self.destination:
			return list()
		else:
			return self.source.get_registers_list() + self.destination.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseConvertInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'CVTDQ2PD' ]
		if name in allowed_instructions:
			super(SseConvertInstruction, self).__init__(name, 'SSE2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(), name, ", ".join(allowed_instructions))
		self.destination = destination
		self.source = source
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()):
			# CVTDQ2PD xmm, xmm/m64: F3 0F E6 /r
			self.size = 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseFloatingPointUnaryInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'RCPPS', 'CVTPD2PS', 'CVTPS2PD' ]
		if name in allowed_instructions:
			super(SseFloatingPointUnaryInstruction, self).__init__(name, 'SSE2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(), name, ", ".join(allowed_instructions))
		self.destination = destination
		self.source = source
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			self.size = 3 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxFloatingPointScalarBinaryInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		single_instructions = [ 'VADDSS', 'VSUBSS', 'VMINSS', 'VMAXSS', 'VMULSS', 'VDIVSS']
		double_instructions = [ 'VADDSD', 'VSUBSD', 'VMINSD', 'VMAXSD', 'VMULSD', 'VDIVSD']
		allowed_instructions = single_instructions + double_instructions
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name in allowed_instructions:
			super(AvxFloatingPointScalarBinaryInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name in single_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address32()):
			# VADDSS xmm, xmm, xmm/m32: VEX.NDS.LIG.F3.0F.WIG 58 /r
			# VSUBSS xmm, xmm, xmm/m32: VEX.NDS.LIG.F3.0F.WIG 5C /r
			# VMULSS xmm, xmm, xmm/m32: VEX.NDS.LIG.F3.0F.WIG 59 /r
			# VDIVSS xmm, xmm, xmm/m32: VEX.NDS.LIG.F3.0F.WIG 5E /r
			# VMINSS xmm, xmm, xmm/m32: VEX.NDS.LIG.F3.0F.WIG 5D /r
			# VMAXSS xmm, xmm, xmm/m32: VEX.NDS.LIG.F3.0F.WIG 5F /r

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		elif name in double_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address64()):
			# VADDSD xmm, xmm, xmm/m64: VEX.NDS.LIG.F2.0F.WIG 58 /r
			# VSUBSD xmm, xmm, xmm/m64: VEX.NDS.LIG.F2.0F.WIG 5C /r
			# VMULSD xmm, xmm, xmm/m64: VEX.NDS.LIG.F2.0F.WIG 59 /r
			# VDIVSD xmm, xmm, xmm/m64: VEX.NDS.LIG.F2.0F.WIG 5E /r
			# VMINSD xmm, xmm, xmm/m64: VEX.NDS.LIG.F2.0F.WIG 5D /r
			# VMAXSD xmm, xmm, xmm/m64: VEX.NDS.LIG.F2.0F.WIG 5F /r

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list() + self.destination.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxFloatingPointVectorBinaryInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = [ 'VADDPS', 'VADDPD', 'VSUBPS', 'VSUBPD',
		                         'VMINPS', 'VMINPD', 'VMAXPS', 'VMAXPD',
		                         'VMULPS', 'VMULPD', 'VDIVPS', 'VDIVPD',
		                         'VANDPS', 'VANDPD', 'VANDNPS', 'VANDNPD',
		                         'VORPS', 'VORPD', 'VXORPS', 'VXORPD',
		                         'VUNPCKLPS', 'VUNPCKLPD', 'VUNPCKHPS', 'VUNPCKHPD',
		                         'VHADDPS', 'VHADDPD', 'VHSUBPS', 'VHSUBPD',
		                         'VADDSUBPS', 'VADDSUBPD']
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name in allowed_instructions:
			super(AvxFloatingPointVectorBinaryInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			# VADDPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 58 /r
			# VADDPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 58 /r

			# VSUBPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 5C /r
			# VSUBPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 5C /r

			# VMULPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 59 /r
			# VMULPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 59 /r

			# VDIVPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 5E /r
			# VDIVPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 5E /r

			# VMINPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 5D /r
			# VMINPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 5D /r

			# VMAXPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 5F /r
			# VMAXPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 5F /r

			# VANDPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 54 /r
			# VANDPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 54 /r

			# VANDNPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 55 /r
			# VANDNPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 55 /r

			# VORPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 56 /r
			# VORPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 56 /r

			# VXORPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 57 /r
			# VXORPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 57 /r

			# VUNPCKLPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 14 /r
			# VUNPCKLPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 14 /r

			# VUNPCKHPS xmm, xmm, xmm/m128: VEX.NDS.128.0F.WIG 15 /r
			# VUNPCKHPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 15 /r

			# VADDSUBPS xmm, xmm, xmm/m128: VEX.NDS.128.F2.0F.WIG D0 /r
			# VADDSUBPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D0 /r
			#   VHADDPS xmm, xmm, xmm/m128: VEX.NDS.128.F2.0F.WIG 7C /r
			#   VHADDPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 7C /r
			#   VHSUBPS xmm, xmm, xmm/m128: VEX.NDS.128.F2.0F.WIG 7D /r
			#   VHSUBPD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 7D /r

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()):
			# VADDPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 58 /r
			# VADDPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 58 /r

			# VSUBPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 5C /r
			# VSUBPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 5C /r

			# VMULPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 59 /r
			# VMULPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 59 /r

			# VDIVPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 5E /r
			# VDIVPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 5E /r

			# VMINPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 5D /r
			# VMINPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 5D /r

			# VMAXPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 5F /r
			# VMAXPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 5F /r

			# VANDPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 54 /r
			# VANDPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 54 /r

			# VANDNPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 55 /r
			# VANDNPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 55 /r

			# VORPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 56 /r
			# VORPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 56 /r

			# VXORPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 57 /r
			# VXORPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 57 /r

			# VUNPCKLPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 14 /r
			# VUNPCKLPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 14 /r

			# VUNPCKHPS ymm, ymm, ymm/m256: VEX.NDS.256.0F.WIG 15 /r
			# VUNPCKHPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 15 /r

			# VADDSUBPS ymm, ymm, ymm/m256: VEX.NDS.256.F2.0F.WIG D0 /r
			# VADDSUBPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D0 /r
			#   VHADDPS ymm, ymm, ymm/m256: VEX.NDS.256.F2.0F.WIG 7C /r
			#   VHADDPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 7C /r
			#   VHSUBPS ymm, ymm, ymm/m256: VEX.NDS.256.F2.0F.WIG 7D /r
			#   VHSUBPD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 7D /r

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))
		
		if self.name in ['VXORPD', 'VXORPS', 'VANDNPD', 'VANDNPS'] and self.source_x == self.source_y and self.source_x == self.destination:
			self.source_x = self.destination
			self.source_y = self.destination

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		if self.name in ['VXORPS', 'VXORPD', 'VANDNPS', 'VANDNPD'] and self.source_x == self.source_y:
			return list()
		else:
			return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxFloatingPointVectorUnaryInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'VCVTPS2PD' ]
		self.destination = destination
		self.source = source
		if name in allowed_instructions:
			super(AvxFloatingPointVectorUnaryInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		elif name == 'VCVTPS2PD' and destination.is_avx_register() and (source.is_sse_register() or source.is_memory_address128()):
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxConvertNarrowInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'VCVTPD2DQ', 'VCVTPD2PS' ]
		self.destination = destination
		self.source = source
		if name in allowed_instructions:
			super(AvxConvertNarrowInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# VCVTPD2DQ xmm, xmm/m128: VEX.128.F2.0F.WIG E6 /r
			# VCVTPD2PS xmm, xmm/m128: VEX.128.66.0F.WIG 5A /r
			
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_avx_register() or source.is_memory_address256()):
			# VCVTPD2DQ xmm, ymm/m256: VEX.256.F2.0F.WIG E6 /r
			# VCVTPD2PS xmm, ymm/m256: VEX.256.66.0F.WIG 5A /r
			
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxFloatingPointVectorReciprocalInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		allowed_instructions = [ 'VRCPPS', 'VRSQRTPS' ]
		self.destination = destination
		self.source = source
		if name in allowed_instructions:
			super(AvxFloatingPointVectorReciprocalInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# VRCPPS   xmm, xmm/m128: VEX.128.0F.WIG 53 /r
			# VRSQRTPS xmm, xmm/m128: VEX.128.0F.WIG 52 /r
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		elif destination.is_avx_register() and (source.is_avx_register() or source.is_memory_address256()):
			# VRCPPS   ymm, ymm/m256: VEX.256.0F.WIG 53 /r
			# VRSQRTPS ymm, ymm/m256: VEX.256.0F.WIG 52 /r
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxFloatingPointScalarReciprocalInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		allowed_instructions = [ 'VRCPSS', 'VRSQRTSS' ]
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name in allowed_instructions:
			super(AvxFloatingPointVectorReciprocalInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address32()):
			# VRCPPS   xmm, xmm/m128: VEX.NDS.LIG.F3.OF.WIG 53 /r
			# VRSQRTPS xmm, xmm/m128: VEX.NDS.LIG.F3.0F.WIG 52 /r
			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxTestInstruction(Instruction):
	def __init__(self, name, source_x, source_y, origin = None):
		allowed_instructions = [ 'VTESTPS', 'VTESTPD', 'VPTEST' ]
		self.source_x = source_x
		self.source_y = source_y
		if name in allowed_instructions:
			super(AvxTestInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			# VTESTPS xmm, xmm/m128: VEX.128.66.0F38.W0 0E /r
			# VTESTPD xmm, xmm/m128: VEX.128.66.0F38.W0 0F /r
			# VPTEST  xmm, xmm/m128: VEX.128.66.0F38.WIG 17 /r
			self.size = source_x.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		elif source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()):
			# VTESTPS ymm, ymm/m256: VEX.256.66.0F38.W0 0E /r
			# VTESTPD ymm, ymm/m256: VEX.256.66.0F38.W0 0F /r
			# VPTEST  ymm, ymm/m256: VEX.256.66.0F38.WIG 17 /r
			self.size = source_x.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return list()

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxVectorRoundInstruction(Instruction):
	def __init__(self, name, destination, source, immediate, origin = None):
		allowed_instructions = [ 'VROUNDPS', 'VROUNDPD' ]
		self.destination = destination
		self.source = source
		self.immediate = immediate
		if name in allowed_instructions:
			super(AvxVectorRoundInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()) and immediate.is_int8():
			# VEX.128.66.0F3A.WIG 08 /r ib
			# VEX.128.66.0F3A.WIG 09 /r ib 
			
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length() + 1
		elif destination.is_avx_register() and (source.is_avx_register() or source.is_memory_address256()) and immediate.is_int8():
			# VEX.256.66.0F3A.WIG 08 /r ib
			# VEX.256.66.0F3A.WIG 09 /r ib 
			
			self.size = source.get_vex_extra_length() + 1 + source.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.immediate)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxFloatingPointCompareInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		vector_instructions = [ 'VCMPEQPS', 'VCMPLTPS', 'VCMPLEPS', 'VCMPUNORDPS',
		                        'VCMPNEQPS', 'VCMPNLTPS', 'VCMPNLEPS', 'VCMPORDPS',
		                        'VCMPEQ_UQPS', 'VCMPNGEPS', 'VCMPNGTPS', 'VCMPFALSEPS'
		                        'VCMPNEQ_OQPS', 'VCMPGEPS', 'VCMPGTPS', 'VCMPTRUEPS',
		                        'VCMPEQ_OSPS', 'VCMPLT_OQPS', 'VCMPLE_OQPS', 'VCMPUNORD_SPS',
		                        'VCMPNEQ_USPS', 'VCMPNLT_UQPS', 'VCMPNLE_UQPS', 'VCMPORD_SPS',
		                        'VCMPEQ_USPS', 'VCMPNGE_UQPS', 'VCMPNGT_UQPS', 'VCMPFALSE_OSPS',
		                        'VCMPNEQ_OSPS', 'VCMPGE_OQPS', 'VCMPGT_OQPS', 'VCMPTRUE_USPS',
		                        'VCMPEQPD', 'VCMPLTPD', 'VCMPLEPD', 'VCMPUNORDPD',
		                        'VCMPNEQPD', 'VCMPNLTPD', 'VCMPNLEPD', 'VCMPORDPD',
		                        'VCMPEQ_UQPD', 'VCMPNGEPD', 'VCMPNGTPD', 'VCMPFALSEPD'
		                        'VCMPNEQ_OQPD', 'VCMPGEPD', 'VCMPGTPD', 'VCMPTRUEPD',
		                        'VCMPEQ_OSPD', 'VCMPLT_OQPD', 'VCMPLE_OQPD', 'VCMPUNORD_SPD',
		                        'VCMPNEQ_USPD', 'VCMPNLT_UQPD', 'VCMPNLE_UQPD', 'VCMPORD_SPD',
		                        'VCMPEQ_USPD', 'VCMPNGE_UQPD', 'VCMPNGT_UQPD', 'VCMPFALSE_OSPD',
		                        'VCMPNEQ_OSPD', 'VCMPGE_OQPD', 'VCMPGT_OQPD', 'VCMPTRUE_USPD' ]
		scalar_float_instructions  =  [ 'VCMPEQSS', 'VCMPLTSS', 'VCMPLESS', 'VCMPUNORDSS',
		                                'VCMPNEQSS', 'VCMPNLTSS', 'VCMPNLESS', 'VCMPORDSS',
		                                'VCMPEQ_UQSS', 'VCMPNGESS', 'VCMPNGTSS', 'VCMPFALSESS'
		                                'VCMPNEQ_OQSS', 'VCMPGESS', 'VCMPGTSS', 'VCMPTRUESS',
		                                'VCMPEQ_OSSS', 'VCMPLT_OQSS', 'VCMPLE_OQSS', 'VCMPUNORD_SSS',
		                                'VCMPNEQ_USSS', 'VCMPNLT_UQSS', 'VCMPNLE_UQSS', 'VCMPORD_SSS',
		                                'VCMPEQ_USSS', 'VCMPNGE_UQSS', 'VCMPNGT_UQSS', 'VCMPFALSE_OSSS',
		                                'VCMPNEQ_OSSS', 'VCMPGE_OQSS', 'VCMPGT_OQSS', 'VCMPTRUE_USSS' ]
		scalar_double_instructions =  [ 'VCMPEQSD', 'VCMPLTSD', 'VCMPLESD', 'VCMPUNORDSD',
		                                'VCMPNEQSD', 'VCMPNLTSD', 'VCMPNLESD', 'VCMPORDSD',
		                                'VCMPEQ_UQSD', 'VCMPNGESD', 'VCMPNGTSD', 'VCMPFALSESD'
		                                'VCMPNEQ_OQSD', 'VCMPGESD', 'VCMPGTSD', 'VCMPTRUESD',
		                                'VCMPEQ_OSSD', 'VCMPLT_OQSD', 'VCMPLE_OQSD', 'VCMPUNORD_SSD',
		                                'VCMPNEQ_USSD', 'VCMPNLT_UQSD', 'VCMPNLE_UQSD', 'VCMPORD_SSD',
		                                'VCMPEQ_USSD', 'VCMPNGE_UQSD', 'VCMPNGT_UQSD', 'VCMPFALSE_OSSD',
		                                'VCMPNEQ_OSSD', 'VCMPGE_OQSD', 'VCMPGT_OQSD', 'VCMPTRUE_USSD' ]
		scalar_instructions = scalar_float_instructions + scalar_double_instructions
		allowed_instructions = vector_instructions + scalar_instructions

		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name in allowed_instructions:
			super(AvxFloatingPointCompareInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name in vector_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			# VCMPPS xmm, xmm, xmm/m128, imm8: VEX.NDS.128.0F.WIG C2 /r ib
			# VCMPPD xmm, xmm, xmm/m128, imm8: VEX.NDS.128.66.0F.WIG C2 /r ib

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		elif name in vector_instructions and destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()):
			# VCMPPS xmm, xmm, xmm/m128, imm8: VEX.NDS.256.0F.WIG C2 /r ib
			# VCMPPD xmm, xmm, xmm/m128, imm8: VEX.NDS.256.66.0F.WIG C2 /r ib

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		elif name in scalar_float_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address32()):
			# VCMPSS xmm, xmm, xmm/m32, imm8: VEX.NDS.LIG.F3.0F.WIG C2 /r ib

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		elif name in scalar_double_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address64()):
			# VCMPSD xmm, xmm, xmm/m64, imm8: VEX.NDS.LIG.F2.0F.WIG C2 /r ib

			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class Fma4ScalarInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, source_z, origin = None):
		single_precision_instructions = [ 'VFMADDSS', 'VFMSUBSS', 'VFNMADDSS', 'VFNMSUBSS' ]
		double_precision_instructions = [ 'VFMADDSD', 'VFMSUBSD', 'VFNMADDSD', 'VFNMSUBSD' ]
		allowed_instructions = single_precision_instructions + double_precision_instructions
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		self.source_z = source_z
		if name in allowed_instructions:
			super(Fma4ScalarInstruction, self).__init__(name, isa_extension = 'FMA4', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name in single_precision_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address32()) and source_z.is_sse_register():
			#  VFMADDSS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 6A /r /is4
			#  VFMSUBSS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 6E /r /is4
			# VFNMADDSS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 7A /r /is4
			# VFNMSUBSS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 7E /r /is4

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif name in single_precision_instructions and destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register() and (source_z.is_sse_register() or source_z.is_memory_address32()):
			#  VFMADDSS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 6A /r /is4
			#  VFMSUBSS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 6E /r /is4
			# VFNMADDSS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 7A /r /is4
			# VFNMSUBSS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 7E /r /is4

			self.size = 3 + 1 + source_z.get_modrm_extra_length()
		elif name in double_precision_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address64()) and source_z.is_sse_register():
			#  VFMADDSD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 6B /r /is4
			#  VFMSUBSD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 6F /r /is4
			# VFNMADDSD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 7B /r /is4
			# VFNMSUBSD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 7F /r /is4

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif name in double_precision_instructions and destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register() and (source_z.is_sse_register() or source_z.is_memory_address64()):
			#  VFMADDSD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 6B /r /is4
			#  VFMSUBSD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 6F /r /is4
			# VFNMADDSD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 7B /r /is4
			# VFNMSUBSD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 7F /r /is4

			self.size = 3 + 1 + source_z.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y, source_z))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}".format(self.name, self.destination, self.source_x, self.source_y, self.source_z)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list() + self.source_z.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		elif self.source_z.is_constant():
			return self.source_z.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		elif self.source_z.is_local_variable():
			return self.source_z.variable
		else:
			return None

class Fma4VectorInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, source_z, origin = None):
		allowed_instructions = [ 'VFMADDPS', 'VFMADDPD', 'VFMSUBPS', 'VFMSUBPD',
		                         'VFNMADDPS', 'VFNMADDPD', 'VFNMSUBPS', 'VFNMSUBPD',
		                         'VFMADDSUBPS', 'VFMADDSUBPD', 'VFMSUBADDPS', 'VFMSUBADDPS']
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		self.source_z = source_z
		if name in allowed_instructions:
			super(Fma4VectorInstruction, self).__init__(name, isa_extension = 'FMA4', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()) and source_z.is_sse_register():
			# VFMADDPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 68 /r /is4
			# VFMADDPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 69 /r /is4

			# VFMSUBPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 6C /r /is4
			# VFMSUBPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 6D /r /is4

			# VFNMADDPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 78 /r /is4
			# VFNMADDPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 79 /r /is4

			# VFNMSUBPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 7C /r /is4
			# VFNMSUBPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 7D /r /is4

			# VFMADDSUBPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 5C /r /is4
			# VFMADDSUBPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 5D /r /is4

			# VFMSUBADDPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 5E /r /is4
			# VFMSUBADDPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 5F /r /is4

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register() and (source_z.is_sse_register() or source_z.is_memory_address128()):
			# VFMADDPS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 68 /r /is4
			# VFMADDPD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 69 /r /is4

			# VFMSUBPS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 6C /r /is4
			# VFMSUBPD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 6D /r /is4

			# VFNMADDPS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 78 /r /is4
			# VFNMADDPD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 79 /r /is4

			# VFNMSUBPS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 7C /r /is4
			# VFNMSUBPD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 7D /r /is4

			# VFMADDSUBPS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 5C /r /is4
			# VFMADDSUBPD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 5D /r /is4

			# VFMSUBADDPS xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 5E /r /is4
			# VFMSUBADDPD xmm, xmm, xmm, xmm/m128: VEX.NDS.128.66.0F3A.W1 5F /r /is4

			self.size = 3 + 1 + source_z.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) and source_z.is_avx_register():
			# VFMADDPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 68 /r /is4
			# VFMADDPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 69 /r /is4

			# VFMSUBPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 6C /r /is4
			# VFMSUBPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 6D /r /is4

			# VFNMADDPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 78 /r /is4
			# VFNMADDPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 79 /r /is4

			# VFNMSUBPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 7C /r /is4
			# VFNMSUBPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 7D /r /is4

			# VFMADDSUBPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 5C /r /is4
			# VFMADDSUBPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 5D /r /is4

			# VFMSUBADDPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 5E /r /is4
			# VFMSUBADDPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 5F /r /is4

			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and source_y.is_avx_register() and (source_z.is_avx_register() or source_z.is_memory_address256()):
			# VFMADDPS ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 68 /r /is4
			# VFMADDPD ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 69 /r /is4

			# VFMSUBPS ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 6C /r /is4
			# VFMSUBPD ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 6D /r /is4

			# VFNMADDPS ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 78 /r /is4
			# VFNMADDPD ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 79 /r /is4

			# VFNMSUBPS ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 7C /r /is4
			# VFNMSUBPD ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 7D /r /is4

			# VFMADDSUBPS ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 5C /r /is4
			# VFMADDSUBPD ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 5D /r /is4

			# VFMSUBADDPS ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 5E /r /is4
			# VFMSUBADDPD ymm, ymm, ymm, ymm/m256: VEX.NDS.256.66.0F3A.W1 5F /r /is4

			self.size = 3 + 1 + source_z.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}'.format(name, destination, source_x, source_y, source_z))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}".format(self.name, self.destination, self.source_x, self.source_y, self.source_z)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list() + self.source_z.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		elif self.source_z.is_constant():
			return self.source_z.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		elif self.source_z.is_local_variable():
			return self.source_z.variable
		else:
			return None

class Fma3Instruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		vector_instructions = [ 'VFMADD132PS', 'VFMADD213PS', 'VFMADD231PS',
		                        'VFMADD132PD', 'VFMADD213PD', 'VFMADD231PD',
		                        'VFMSUB132PS', 'VFMSUB213PS', 'VFMSUB231PS',
		                        'VFMSUB132PD', 'VFMSUB213PD', 'VFMSUB231PD',
		                        'VFNMADD132PS', 'VFNMADD213PS', 'VFNMADD231PS',
		                        'VFNMADD132PD', 'VFNMADD213PD', 'VFNMADD231PD',
		                        'VFNMSUB132PS', 'VFNMSUB213PS', 'VFNMSUB231PS',
		                        'VFNMSUB132PD', 'VFNMSUB213PD', 'VFNMSUB231PD',
		                        'VFMADDSUB132PS', 'VFMADDSUB213PS', 'VFMADDSUB231PS',
		                        'VFMADDSUB132PD', 'VFMADDSUB213PD', 'VFMADDSUB231PD',
		                        'VFMSUBADD132PS', 'VFMSUBADD213PS', 'VFMSUBADD231PS',
		                        'VFMSUBADD132PD', 'VFMSUBADD213PD', 'VFMSUBADD231PD' ]
		single_instructions = [ 'VFMADD132SS', 'VFMADD213SS', 'VFMADD231SS',
		                        'VFMSUB132SS', 'VFMSUB213SS', 'VFMSUB231SS',
		                        'VFNMADD132SS', 'VFNMADD213SS', 'VFNMADD231SS',
		                        'VFNMSUB132SS', 'VFNMSUB213SS', 'VFNMSUB231SS',
		                        'VFMADDSUB132SS', 'VFMADDSUB213SS', 'VFMADDSUB231SS',
		                        'VFMSUBADD132SS', 'VFMSUBADD213SS', 'VFMSUBADD231SS' ]
		double_instructions = [ 'VFMADD132SD', 'VFMADD213SD', 'VFMADD231SD',
		                        'VFMSUB132SD', 'VFMSUB213SD', 'VFMSUB231SD',
		                        'VFNMADD132SD', 'VFNMADD213SD', 'VFNMADD231SD',
		                        'VFNMSUB132SD', 'VFNMSUB213SD', 'VFNMSUB231SD',
		                        'VFMADDSUB132SD', 'VFMADDSUB213SD', 'VFMADDSUB231SD',
		                        'VFMSUBADD132SD', 'VFMSUBADD213SD', 'VFMSUBADD231SD' ]
		allowed_instructions = vector_instructions + single_instructions + double_instructions
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if name in allowed_instructions:
			super(Fma3Instruction, self).__init__(name, isa_extension = 'FMA3', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if name in vector_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif name in single_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address32()):
			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif name in double_instructions and destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address64()):
			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		elif name in vector_instructions and destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()):
			self.size = 3 + 1 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class MmxSseIntegerBinaryInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		mmx_instructions = [ 'PADDB', 'PADDW', 'PADDD', 'PSUBB', 'PSUBW', 'PSUBD',
		                     'PADDSB', 'PADDSW', 'PADDUSB', 'PADDUSW',
		                     'PSUBSB', 'PSUBSW', 'PSUBUSB', 'PSUBUSW',
		                     'PAND', 'PANDN', 'POR', 'PXOR',
		                     'PCMPEQB', 'PCMPEQW', 'PCMPEQD', 'PCMPGTB', 'PCMPGTW', 'PCMPGTD',
		                     'PMULLW', 'PMULHW', 'PMADDWD',
		                     'PUNPCKLBW', 'PUNPCKHBW', 'PUNPCKLWD', 'PUNPCKHWD', 'PUNPCKLDQ', 'PUNPCKHDQ',
		                     'PACKSSWB', 'PACKSSDW', 'PACKUSWB']
		mmx2_instructions = [ 'PAVGB', 'PAVGW', 'PMAXUB', 'PMAXSW', 'PMINUB', 'PMINSW', 'PSADBW', 'PMULHUW' ]
		sse2_instructions =  [ 'PADDQ', 'PSUBQ', 'PMULUDQ' ]
		sse2_xmm_instructions = [ 'PUNPCKLQDQ', 'PUNPCKHQDQ' ]
		ssse3_instructions = [ 'PSIGNB', 'PSIGNW', 'PSIGND',
		                       'PHADDW', 'PHADDD', 'PHSUBW', 'PHSUBD', 'PHADDSW', 'PHSUBSW',
		                       'PSHUFB', 'PMULHRSW', 'PMADDUBSW']
		sse41_instructions = [ 'PCMPEQQ', 'PACKUSDW', 'PTEST',
		                       'PMULLD', 'PMULDQ',
		                       'PMAXSB', 'PMAXSD', 'PMAXUW', 'PMAXUD',
		                       'PMINSB', 'PMINSD', 'PMINUW', 'PMINUD', 'PHMINPOSUW']
		sse42_instructions = [ 'PCMPGTQ' ]
		allowed_mmx_instructions = mmx_instructions + mmx2_instructions + sse2_instructions + ssse3_instructions
		allowed_xmm_instructions = allowed_mmx_instructions + sse2_xmm_instructions + sse41_instructions + sse42_instructions 
		if name not in allowed_xmm_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_xmm_instructions)))
		if name in allowed_mmx_instructions and destination.is_mmx_register() and (source.is_mmx_register() or source.is_memory_address64()):
			# PADDB mm, mm/m64: 0F FC /r
			# PADDW mm, mm/m64: 0F FD /r
			# PADDD mm, mm/m64: 0F FE /r
			# PADDQ mm, mm/m64: 0F D4 /r

			# PSUBB mm, mm/m64: 0F F8 /r
			# PSUBW mm, mm/m64: 0F F9 /r
			# PSUBD mm, mm/m64: 0F FA /r
			# PSUBQ mm, mm/m64: 0F FB /r

			#  PADDSB mm, mm/m64: 0F EC /r
			#  PADDSW mm, mm/m64: 0F ED /r
			# PADDUSB mm, mm/m64: 0F DC /r
			# PADDUSW mm, mm/m64: 0F DD /r

			#  PSUBSB mm, mm/m64: 0F E8 /r
			#  PSUBSW mm, mm/m64: 0F E9 /r
			# PSUBUSB mm, mm/m64: 0F D8 /r
			# PSUBUSW mm, mm/m64: 0F D9 /r

			#  PAVGB mm, mm/m64: 0F E0 /r
			#  PAVGW mm, mm/m64: 0F E3 /r
			# PMAXUB mm, mm/m64: 0F DE /r
			# PMAXSW mm, mm/m64: 0F EE /r
			# PMINUB mm, mm/m64: 0F DA /r
			# PMINSW mm, mm/m64: 0F EA /r

			#  PAND mm, mm/m64: 0F DB /r
			# PANDN mm, mm/m64: 0F DF /r
			#   POR mm, mm/m64: 0F EB /r
			#  PXOR mm, mm/m64: 0F EF /r

			# PCMPEQB mm, mm/m64: 0F 74 /r
			# PCMPEQW mm, mm/m64: 0F 75 /r
			# PCMPEQD mm, mm/m64: 0F 76 /r
			# PCMPGTB mm, mm/m64: 0F 64 /r
			# PCMPGTW mm, mm/m64: 0F 65 /r
			# PCMPGTD mm, mm/m64: 0F 66 /r

			# PMULUDQ mm, mm/m64: 66 0F F4 /r
			#  PMULLW mm, mm/m64: 66 0F D5 /r
			#  PMULHW mm, mm/m64: 66 0F E5 /r
			# PMULHUW mm, mm/m64: 66 0F E4 /r

			# PUNPCKLBW mm, mm/m64: 0F 60 /r
			# PUNPCKHBW mm, mm/m64: 0F 68 /r
			# PUNPCKLWD mm, mm/m64: 0F 61 /r
			# PUNPCKHWD mm, mm/m64: 0F 69 /r
			# PUNPCKLDQ mm, mm/m64: 0F 62 /r
			# PUNPCKHDQ mm, mm/m64: 0F 6A /r

			# PUNPCKLQDQ mm, mm/m64: 0F 6C /r
			# PUNPCKHQDQ mm, mm/m64: 0F 6D /r
			#   PACKSSWB mm, mm/m64: 0F 63 /r
			#   PACKSSDW mm, mm/m64: 0F 6B /r
			#   PACKUSWB mm, mm/m64: 0F 67 /r

			# PSIGNB mm, mm/m64: 0F 38 08 /r
			# PSIGNW mm, mm/m64: 0F 38 09 /r
			# PSIGND mm, mm/m64: 0F 38 0A /r

			#  PHADDW mm, mm/m64: 0F 38 01 /r
			#  PHADDD mm, mm/m64: 0F 38 02 /r
			# PHADDSW mm, mm/m64: 0F 38 03 /r
			#  PHSUBW mm, mm/m64: 0F 38 05 /r
			#  PHSUBD mm, mm/m64: 0F 38 06 /r
			# PHSUBSW mm, mm/m64: 0F 38 07 /r

			#    PSHUFB mm, mm/m64: 0F 38 00 /r
			#  PMULHRSW mm, mm/m64: 0F 38 0B /r
			# PMADDUBSW mm, mm/m64: 0F 38 04 /r

			if name in mmx_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'MMX', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 4 + source.get_modrm_extra_length()
			elif name in mmx2_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'MMX+', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 4 + source.get_modrm_extra_length()
			elif name in sse2_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSE2', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 4 + source.get_modrm_extra_length()
			elif name in ssse3_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSSE3', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
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

			if name in (mmx_instructions + mmx2_instructions + sse2_instructions + sse2_xmm_instructions):
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSE2', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 4 + source.get_modrm_extra_length()
			elif name in ssse3_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSSE3', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 5 + source.get_modrm_extra_length()
			elif name in sse41_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSE4.1', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 5 + source.get_modrm_extra_length()
			elif name in sse42_instructions:
				super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSE4.2', origin = origin)
				self.destination = destination
				self.source = source
				self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

		if self.name in ['PANDN', 'PXOR',
		                 'PCMPEQB', 'PCMPEQW', 'PCMPEQD', 'PCMPEQQ',
		                 'PCMPGTB', 'PCMPGTW', 'PCMPGTD', 'PCMPGTQ'] and self.destination == self.source:
			self.source = self.destination

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		if self.name in ['PANDN', 'PXOR',
		                 'PCMPEQB', 'PCMPEQW', 'PCMPEQD', 'PCMPEQQ',
		                 'PCMPGTB', 'PCMPGTW', 'PCMPGTD', 'PCMPGTQ'] and self.destination == self.source:
			return list()
		else:
			return self.destination.get_registers_list() + self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.name not in ['PTEST']:
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseIntegerUnaryInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		ssse3_instructions = [ 'PABSB', 'PABSW', 'PABSD' ]
		aes_instructions = [ 'AESIMC', 'AESENC', 'AESENCLAST', 'AESDEC', 'AESDECLAST' ]
		allowed_instructions = ssse3_instructions + aes_instructions
		if name in ssse3_instructions:
			super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'SSSE3', origin = origin)
		elif name in aes_instructions:
			super(MmxSseIntegerBinaryInstruction, self).__init__(name, isa_extension = 'AES', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		self.destination = destination
		self.source = source
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			#  PABSB xmm, xmm/m128: 66 0F 38 1C /r
			#  PABSW xmm, xmm/m128: 66 0F 38 1D /r
			#  PABSD xmm, xmm/m128: 66 0F 38 1E /r

			#     AESIMC xmm, xmm/m128: 66 0F 38 DB /r
			#     AESENC xmm, xmm/m128: 66 0F 38 DC /r
			# AESENCLAST xmm, xmm/m128: 66 0F 38 DD /r
			#     AESDEC xmm, xmm/m128: 66 0F 38 DE /r
			# AESDECLAST xmm, xmm/m128: 66 0F 38 DF /r

			self.size = 1 + 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

		if self.name in ['PANDN', 'PXOR',
		                 'PCMPEQB', 'PCMPEQW', 'PCMPEQD', 'PCMPEQQ',
		                 'PCMPGTB', 'PCMPGTW', 'PCMPGTD', 'PCMPGTQ'] and self.destination == self.source:
			self.source = self.destination

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		if self.name not in ['PTEST']:
			return [self.destination.register]
		else:
			return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxIntegerInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		avx_instructions = [ 'VPADDB', 'VPADDW', 'VPADDD', 'VPADDQ',
		                     'VPSUBB', 'VPSUBW', 'VPSUBD', 'VPSUBQ',
		                     'VPADDSB', 'VPADDSW', 'VPADDUSB', 'VPADDUSW',
		                     'VPSUBSB', 'VPSUBSW', 'VPSUBUSB', 'VPSUBUSW',
		                     'VPMAXUB', 'VPMAXUW', 'VPMAXUD',
		                     'VPMINUB', 'VPMINUW', 'VPMINUD',
		                     'VPMAXSB', 'VPMINSW', 'VPMAXSD',
		                     'VPMINSB', 'VPMAXSW', 'VPMINSD',
		                     'VPAVGB', 'VPAVGW',
		                     'VPSADBW',
		                     'VPAND', 'VPANDN', 'VPOR', 'VPXOR',
		                     'VPCMPEQB', 'VPCMPEQW', 'VPCMPEQD', 'VPCMPEQQ',
		                     'VPCMPGTB', 'VPCMPGTW', 'VPCMPGTD','VPCMPGTQ',
		                     'VPMULUDQ', 'VPMULLW', 'VPMULHW', 'VPMULHUW', 'VPMADDWD',
		                     'VPUNPCKLBW', 'VPUNPCKLWD', 'VPUNPCKLDQ', 'VPUNPCKLQDQ',
		                     'VPUNPCKHBW', 'VPUNPCKHWD', 'VPUNPCKHDQ', 'VPUNPCKHQDQ',
		                     'VPACKSSWB',  'VPACKSSDW',  'VPACKUSWB',  'VPACKUSDW',
		                     'VPSIGNB', 'VPSIGNW', 'VPSIGND',
		                     'VPHADDW', 'VPHADDD', 'VPHADDSW',
		                     'VPHSUBW', 'VPHSUBD', 'VPHSUBSW',
		                     'VPSHUFB', 'VPMULHRSW', 'VPMADDUBSW',
		                     'VPMULLD', 'VPMULDQ' ]
		if name not in avx_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(avx_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			# VPADDB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG FC /r
			# VPADDW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG FD /r
			# VPADDD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG FE /r
			# VPADDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D4 /r

			# VPSUBB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG F8 /r
			# VPSUBW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG F9 /r
			# VPSUBD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG FA /r
			# VPSUBQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG FB /r

			#  VPADDSB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG EC /r
			#  VPADDSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG ED /r
			# VPADDUSB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG DC /r
			# VPADDUSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG DD /r

			#  VPSUBSB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E8 /r
			#  VPSUBSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E9 /r
			# VPSUBUSB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D8 /r
			# VPSUBUSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D9 /r

			#  VPAVGB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E0 /r
			#  VPAVGW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E3 /r

			# VPMAXUB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG DE /r
			# VPMAXUW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 3E /r
			# VPMAXUD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 3F /r

			# VPMINUB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG DA /r
			# VPMINUW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 3A /r
			# VPMINUD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 3B /r

			# VPMAXSB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 3C /r
			# VPMAXSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG EE /r
			# VPMAXSD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 3D /r

			# VPMINSB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 38 /r
			# VPMINSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG EA /r
			# VPMINSD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 39 /r

			#  VPAND xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG DB /r
			# VPANDN xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG DF /r
			#   VPOR xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG EB /r
			#  VPXOR xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG EF /r

			# VPCMPEQB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 74 /r
			# VPCMPEQW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 75 /r
			# VPCMPEQD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 76 /r
			# VPCMPEQQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 29 /r

			# VPCMPGTB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 64 /r
			# VPCMPGTW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 65 /r
			# VPCMPGTD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 66 /r
			# VPCMPGTQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 37 /r

			# VPMULUDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG F4 /r
			#  VPMULLW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D5 /r
			#  VPMULHW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E5 /r
			# VPMULHUW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E4 /r

			#  VPUNPCKLBW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 60 /r
			#  VPUNPCKLWD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 61 /r
			#  VPUNPCKLDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 62 /r
			# VPUNPCKLQDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 6C /r

			#  VPUNPCKHBW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 68 /r
			#  VPUNPCKHWD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 69 /r
			#  VPUNPCKHDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 6A /r
			# VPUNPCKHQDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 6D /r

			#   VPACKSSWB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 63 /r
			#   VPACKSSDW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 6B /r
			#   VPACKUSWB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG 67 /r
			#   VPACKUSDW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 2B /r

			# VPSIGNB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 08 /r
			# VPSIGNW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 09 /r
			# VPSIGND xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 0A /r

			#  VPHADDW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 01 /r
			#  VPHADDD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 02 /r
			# VPHADDSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 03 /r
			#  VPHSUBW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 05 /r
			#  VPHSUBD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 06 /r
			# VPHSUBSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 07 /r

			#    VPSHUFB xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 00 /r
			#  VPMULHRSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 0B /r
			# VPMADDUBSW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 04 /r

			#   VPMULLD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 40 /r
			#   VPMULDQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.WIG 28 /r

			super(AvxIntegerInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.size = 4 + source_y.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()):
			# VPADDB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG FC /r
			# VPADDW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG FD /r
			# VPADDD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG FE /r
			# VPADDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D4 /r

			# VPSUBB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG F8 /r
			# VPSUBW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG F9 /r
			# VPSUBD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG FA /r
			# VPSUBQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG FB /r

			#  VPADDSB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG EC /r
			#  VPADDSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG ED /r
			# VPADDUSB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG DC /r
			# VPADDUSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG DD /r

			#  VPSUBSB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E8 /r
			#  VPSUBSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E9 /r
			# VPSUBUSB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D8 /r
			# VPSUBUSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D9 /r

			#  VPAVGB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E0 /r
			#  VPAVGW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E3 /r

			# VPMAXUB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG DE /r
			# VPMAXUW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 3E /r
			# VPMAXUD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 3F /r

			# VPMINUB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG DA /r
			# VPMINUW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 3A /r
			# VPMINUD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 3B /r

			# VPMAXSB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 3C /r
			# VPMAXSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG EE /r
			# VPMAXSD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 3D /r

			# VPMINSB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 38 /r
			# VPMINSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG EA /r
			# VPMINSD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 39 /r

			#  VPAND ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG DB /r
			# VPANDN ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG DF /r
			#   VPOR ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG EB /r
			#  VPXOR ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG EF /r

			# VPCMPEQB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 74 /r
			# VPCMPEQW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 75 /r
			# VPCMPEQD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 76 /r
			# VPCMPEQQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 29 /r

			# VPCMPGTB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 64 /r
			# VPCMPGTW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 65 /r
			# VPCMPGTD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 66 /r
			# VPCMPGTQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 37 /r

			# VPMULUDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG F4 /r
			#  VPMULLW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D5 /r
			#  VPMULHW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E5 /r
			# VPMULHUW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E4 /r

			#  VPUNPCKLBW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 60 /r
			#  VPUNPCKLWD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 61 /r
			#  VPUNPCKLDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 62 /r
			# VPUNPCKLQDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 6C /r

			#  VPUNPCKHBW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 68 /r
			#  VPUNPCKHWD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 69 /r
			#  VPUNPCKHDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 6A /r
			# VPUNPCKHQDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 6D /r

			#   VPACKSSWB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 63 /r
			#   VPACKSSDW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 6B /r
			#   VPACKUSWB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG 67 /r
			#   VPACKUSDW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 2B /r

			# VPSIGNB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 08 /r
			# VPSIGNW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 09 /r
			# VPSIGND ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 0A /r

			#  VPHADDW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 01 /r
			#  VPHADDD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 02 /r
			# VPHADDSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 03 /r
			#  VPHSUBW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 05 /r
			#  VPHSUBD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 06 /r
			# VPHSUBSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 07 /r

			#    VPSHUFB ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 00 /r
			#  VPMULHRSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 0B /r
			# VPMADDUBSW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 04 /r

			#   VPMULLD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 40 /r
			#   VPMULDQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.WIG 28 /r

			super(AvxIntegerInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.size = 4 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

		if self.name in [ 'VPANDN', 'VPXOR',
		                  'VPCMPEQB', 'VPCMPEQW', 'VPCMPEQD', 'VPCMPEQQ',
		                  'VPCMPGTB', 'VPCMPGTW', 'VPCMPGTD', 'VPCMPGTQ' ] and self.source_x == self.source_y and self.source_x == self.destination:
			self.source_x = self.destination
			self.source_y = self.destination

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		if self.name in ['VPANDN', 'VPXOR',
		                 'VPCMPEQB', 'VPCMPEQW', 'VPCMPEQD', 'VPCMPEQQ',
		                 'VPCMPGTB', 'VPCMPGTW', 'VPCMPGTD', 'VPCMPGTQ']:
			if self.source_x == self.source_y:
				return list()
			else:
				return self.source_x.get_registers_list() + self.source_y.get_registers_list()
		else:
			return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class XopHorizontalAddInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		xop_instructions = [ 'VPHADDBW',  'VPHADDBD',  'VPHADDBQ',  'VPHADDWD',  'VPHADDWQ',  'VPHADDDQ',
		                     'VPHADDUBW', 'VPHADDUBD', 'VPHADDUBQ', 'VPHADDUWD', 'VPHADDUWQ', 'VPHADDUDQ',
		                     'VPHSUBBW',  'VPHSUBWD',  'VPHSUBDQ' ]
		if name in xop_instructions:
			super(XopHorizontalAddInstruction, self).__init__(name, isa_extension = 'XOP', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(xop_instructions)))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			# VPHADDBW xmm, xmm/m128
			# VPHADDBD xmm, xmm/m128
			# VPHADDBQ xmm, xmm/m128
			# VPHADDWD xmm, xmm/m128
			# VPHADDWQ xmm, xmm/m128
			# VPHADDDQ xmm, xmm/m128

			# VPHADDUBW xmm, xmm/m128
			# VPHADDUBD xmm, xmm/m128
			# VPHADDUBQ xmm, xmm/m128
			# VPHADDUWD xmm, xmm/m128
			# VPHADDUWQ xmm, xmm/m128
			# VPHADDUDQ xmm, xmm/m128

			# VPHSUBBW xmm, xmm/m128
			# VPHSUBWD xmm, xmm/m128
			# VPHSUBDQ xmm, xmm/m128

			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseAvxDuplicateInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		single_instructions = [ 'MOVSLDUP', 'MOVSHDUP', 'VMOVSLDUP', 'VMOVSHDUP']
		double_instructions = [ 'MOVDDUP', 'VMOVDDUP' ]
		duplicate_instructions = single_instructions + double_instructions
		sse3_instructions = [ 'MOVSLDUP', 'MOVSHDUP', 'MOVDDUP' ]
		avx_instructions = [ 'VMOVSLDUP', 'VMOVSHDUP', 'VMOVDDUP' ]
		if name in sse3_instructions:
			super(SseAvxDuplicateInstruction, self).__init__(name, isa_extension = 'SSE3', origin = origin)
		elif name in avx_instructions:
			super(SseAvxDuplicateInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(duplicate_instructions)))
		self.destination = destination
		self.source = source
		if name in double_instructions and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()):
			#  MOVDDUP xmm, xmm/m64: F2 0F 12 /r
			# VMOVDDUP xmm, xmm/m64: VEX.128.F2.0F.WIG 12 /r

			if name in avx_instructions:
				self.size = 4 + source.get_modrm_extra_length()
			else:
				self.size = 4 + source.get_modrm_extra_length()
		elif name in single_instructions and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()):
			#  MOVSLDUP xmm, xmm/m64: F3 0F 12 /r
			#  MOVSHDUP xmm, xmm/m64: F3 0F 16 /r
			# VMOVSLDUP xmm, xmm/m128: VEX.128.F3.0F.WIG 12 /r
			# VMOVSHDUP xmm, xmm/m128: VEX.128.F3.0F.WIG 16 /r

			if name in avx_instructions:
				self.size = 4 + source.get_modrm_extra_length()
			else:
				self.size = 4 + source.get_modrm_extra_length()
		elif name in avx_instructions and destination.is_avx_register() and (source.is_avx_register() or source.is_memory_address256()):
			# VMOVDDUP  ymm, ymm/m256: VEX.256.F2.0F.WIG 12 /r
			# VMOVSLDUP ymm, ymm/m256: VEX.256.F3.0F.WIG 16 /r
			# VMOVSHDUP ymm, ymm/m256: VEX.256.F3.0F.WIG 12 /r

			self.size = 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxBroadcastInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		broadcast_instructions = [ 'VBROADCASTSS', 'VBROADCASTSD', 'VBROADCASTF128', 'VPBROADCASTB', 'VPBROADCASTW', 'VPBROADCASTD', 'VPBROADCASTQ', 'VBROADCASTI128' ]
		if name not in broadcast_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(broadcast_instructions)))
		if name == 'VPBROADCASTB' and (destination.is_sse_register() or destination.is_avx_register()) and (source.is_sse_register() or source.is_memory_address8()):
			# VPBROADCASTB xmm, xmm/m8: VEX.128.66.0F38.W0 78 /r
			# VPBROADCAST8 ymm, xmm/m8: VEX.256.66.0F38.W0 78 /r 

			super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 4 + source.get_modrm_extra_length()
		elif name == 'VPBROADCASTW' and (destination.is_sse_register() or destination.is_avx_register()) and (source.is_sse_register() or source.is_memory_address16()):
			# VPBROADCASTW xmm, xmm/m16: VEX.128.66.0F38.W0 79 /r
			# VPBROADCASTW ymm, xmm/m16: VEX.256.66.0F38.W0 79 /r 

			super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 4 + source.get_modrm_extra_length()
		elif name in ('VBROADCASTSS', 'VPBROADCASTD') and (destination.is_sse_register() or destination.is_avx_register()) and (source.is_sse_register() or source.is_memory_address32()):
			# VBROADCASTSS xmm, xmm/m32: VEX.128.66.0F38.W0 18 /r
			# VBROADCASTSS ymm, xmm/m32: VEX.256.66.0F38.W0 18 /r
			# VPBROADCASTD xmm, xmm/m32: VEX.128.66.0F38.W0 58 /r
			# VPBROADCASTD ymm, xmm/m32: VEX.256.66.0F38.W0 58 /r 

			if name == 'VBROADCASTSS' and source.is_memory_address32():
				super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			else:
				super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 4 + source.get_modrm_extra_length()
		elif name == 'VPBROADCASTQ' and (destination.is_sse_register() or destination.is_avx_register()) and (source.is_sse_register() or source.is_memory_address32()):
			# VPBROADCASTQ xmm, xmm/m64: VEX.128.66.0F38.W0 59 /r
			# VPBROADCASTQ ymm, xmm/m64: VEX.256.66.0F38.W0 59 /r 

			super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 4 + source.get_modrm_extra_length()
		elif name == 'VBROADCASTSD' and destination.is_avx_register() and (source.is_sse_register() or source.is_memory_address64()):
			# VBROADCASTSD ymm, xmm/m64: VEX.256.66.0F38.W0 19 /r 

			if source.is_memory_address64():
				super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			else:
				super(AvxBroadcastInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 4 + source.get_modrm_extra_length()
		elif name in ('VBROADCASTF128', 'VBROADCASTI128') and destination.is_avx_register() and source.is_memory_address128():
			# VBROADCASTF128 ymm, m128: VEX.256.66.0F38.W0 1A /r
			# VBROADCASTI128 ymm, m128: VEX.256.66.0F38.W0 5A /r

			self.size = 4 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class MmxSseShiftInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		shift_instructions = [ 'PSLLW', 'PSLLD', 'PSLLQ',
		                       'PSRLW', 'PSRLD', 'PSRLQ',
		                       'PSRAW', 'PSRAD' ]
		if name in shift_instructions:
			super(MmxSseShiftInstruction, self).__init__(name, destination, source, isa_extension = "SSE2", origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(shift_instructions)))
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
		elif destination.is_sse_register() and source.is_uint8():
			# PSLLW xmm, imm8: 66 0F 71 /6 ib
			# PSLLD xmm, imm8: 66 0F 72 /6 ib
			# PSLLQ xmm, imm8: 66 0F 73 /6 ib
			# PSRLW xmm, imm8: 66 0F 71 /2 ib
			# PSRLD xmm, imm8: 66 0F 72 /2 ib
			# PSRLQ xmm, imm8: 66 0F 73 /2 ib
			# PSRAW xmm, imm8: 66 0F 71 /4 ib
			# PSRAD xmm, imm8: 66 0F 72 /4 ib
			self.size = 4 + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list()
		
	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxShiftInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		avx_instructions = ( 'VPSLLW', 'VPSLLD', 'VPSLLQ', 'VPSRLW', 'VPSRLD', 'VPSRLQ', 'VPSRAW', 'VPSRAD' )
		avx2_instructions = ( 'VPSLLVD', 'VPSLLVQ', 'VPSRLVD', 'VPSRLVQ', 'VPSRAVD' )
		shift_instructions = avx_instructions + avx2_instructions
		if name not in shift_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(shift_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			# VPSLLW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG F1 /r
			# VPSLLD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG F2 /r
			# VPSLLQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG F3 /r
			# VPSRLW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D1 /r
			# VPSRLD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D2 /r
			# VPSRLQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG D3 /r
			# VPSRAW xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E1 /r
			# VPSRAD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F.WIG E2 /r

			# VPSLLVD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.W0 47 /r
			# VPSLLVQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.W1 47 /r
			# VPSRLVD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.W0 45 /r
			# VPSRLVQ xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.W1 45 /r
			# VPSRAVD xmm, xmm, xmm/m128: VEX.NDS.128.66.0F38.W0 46 /r

			if name in avx_instructions:
				super(AvxShiftInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			else:
				super(AvxShiftInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.size = 4 + source_y.get_modrm_extra_length()
		elif name in avx_instructions and destination.is_sse_register() and source_x.is_sse_register() and source_y.is_uint8():
			# VPSLLW xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 71 /6 ib
			# VPSLLD xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 72 /6 ib
			# VPSLLQ xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 73 /6 ib
			# VPSRLW xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 71 /2 ib
			# VPSRLD xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 72 /2 ib
			# VPSRLQ xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 73 /2 ib
			# VPSRAW xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 71 /4 ib
			# VPSRAD xmm, xmm, imm8: VEX.NDD.128.66.0F.WIG 72 /4 ib

			super(AvxShiftInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.size = 4 + 1
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()):
			# VPSLLW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG F1 /r
			# VPSLLD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG F2 /r
			# VPSLLQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG F3 /r
			# VPSRLW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D1 /r
			# VPSRLD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D2 /r
			# VPSRLQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG D3 /r
			# VPSRAW ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E1 /r
			# VPSRAD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F.WIG E2 /r

			# VPSLLVD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W0 47 /r
			# VPSLLVQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W1 47 /r
			# VPSRLVD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W0 45 /r
			# VPSRLVQ ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W1 45 /r
			# VPSRAVD ymm, ymm, ymm/m256: VEX.NDS.256.66.0F38.W0 46 /r

			super(AvxShiftInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.size = 4 + source_y.get_modrm_extra_length()
		elif name in avx_instructions and destination.is_avx_register() and source_x.is_avx_register() and source_y.is_uint8():
			# VPSLLW ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 71 /6 ib
			# VPSLLD ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 72 /6 ib
			# VPSLLQ ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 73 /6 ib
			# VPSRLW ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 71 /2 ib
			# VPSRLD ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 72 /2 ib
			# VPSRLQ ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 73 /2 ib
			# VPSRAW ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 71 /4 ib
			# VPSRAD ymm, ymm, imm8: VEX.NDD.256.66.0F.WIG 72 /4 ib

			super(AvxShiftInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.size = 4 + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class XopShiftRotateInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, origin = None):
		shift_instructions = ( 'VPSHLB', 'VPSHLW', 'VPSHLD', 'VPSHLQ',
		                       'VPSHAB', 'VPSHAW', 'VPSHAD', 'VPSHAQ' )
		rotate_instructions = ( 'VPROTB', 'VPROTW', 'VPROTD', 'VPROTQ' )
		allowed_instructions = shift_instructions + rotate_instructions
		if name in allowed_instructions:
			super(XopShiftRotateInstruction, self).__init__(name, isa_extension = 'XOP', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		self.destination = destination
		self.source_x = source_x
		self.source_y = source_y
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()):
			# VPSHLB xmm, xmm, xmm/m128
			# VPSHLW xmm, xmm, xmm/m128
			# VPSHLD xmm, xmm, xmm/m128
			# VPSHLQ xmm, xmm, xmm/m128

			# VPSHAB xmm, xmm, xmm/m128
			# VPSHAW xmm, xmm, xmm/m128
			# VPSHAD xmm, xmm, xmm/m128
			# VPSHAQ xmm, xmm, xmm/m128

			# VPROTB xmm, xmm, xmm/m128
			# VPROTW xmm, xmm, xmm/m128
			# VPROTD xmm, xmm, xmm/m128
			# VPROTQ xmm, xmm, xmm/m128

			self.size = 4 + source_y.get_modrm_extra_length()
		elif destination.is_sse_register() and (source_x.is_sse_register() or source_x.is_memory_address128()) and source_y.is_sse_register():
			# VPSHLB xmm, xmm/m128, xmm
			# VPSHLW xmm, xmm/m128, xmm
			# VPSHLD xmm, xmm/m128, xmm
			# VPSHLQ xmm, xmm/m128, xmm

			# VPSHAB xmm, xmm/m128, xmm
			# VPSHAW xmm, xmm/m128, xmm
			# VPSHAD xmm, xmm/m128, xmm
			# VPSHAQ xmm, xmm/m128, xmm

			# VPROTB xmm, xmm/m128, xmm
			# VPROTW xmm, xmm/m128, xmm
			# VPROTD xmm, xmm/m128, xmm
			# VPROTQ xmm, xmm/m128, xmm

			self.size = 4 + source_x.get_modrm_extra_length()
		elif name in rotate_instructions and destination.is_sse_register() and (source_x.is_sse_register() or source_x.is_memory_address128()) and source_y.is_int8():
			# VPROTB xmm, xmm/m128, imm8
			# VPROTW xmm, xmm/m128, imm8
			# VPROTD xmm, xmm/m128, imm8
			# VPROTQ xmm, xmm/m128, imm8

			self.size = 4 + source_x.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source_x, source_y))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source_x, self.source_y)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_x.is_constant():
			return self.source_x.constant
		elif self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_x.is_local_variable():
			return self.source_x.variable
		elif self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class MmxSseShuffleInstruction(Instruction):
	def __init__(self, name, destination, source, immediate, origin = None):
		mmx_shuffle_instructions = ['PSHUFW']
		sse_shuffle_instructions = ['SHUFPS']
		sse2_shuffle_instructions = ['SHUFPD', 'PSHUFD', 'PSHUFLW', 'PSHUFHW']
		if name in mmx_shuffle_instructions:
			super(MmxSseShuffleInstruction, self).__init__(name, isa_extension = "MMX+", origin = origin)
		elif name in sse_shuffle_instructions:
			super(MmxSseShuffleInstruction, self).__init__(name, isa_extension = "SSE", origin = origin)
		elif name in sse2_shuffle_instructions:
			super(MmxSseShuffleInstruction, self).__init__(name, isa_extension = "SSE2", origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the MMX/SSE shuffle instructions ({1})'.format(name, ", ".join(mmx_shuffle_instructions + sse_shuffle_instructions + sse2_shuffle_instructions)))
		self.destination = destination
		self.source = source
		self.immediate = immediate
		if name in mmx_shuffle_instructions and destination.is_mmx_register() and (source.is_mmx_register() or source.is_memory_address64()) and immediate.is_uint8():
			# PSHUFW mm, mm/m64, imm8: 0F 70 /r ib

			self.size = 3 + 1 + source.get_modrm_extra_length()
		elif name in (sse_shuffle_instructions + sse2_shuffle_instructions) and destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()) and immediate.is_uint8():
			# PSHUFLW xmm, xmm/m128, imm8: F2 0F 70 /r ib
			# PSHUFHW xmm, xmm/m128, imm8: F3 0F 70 /r ib
			# PSHUFD  xmm, xmm/m128, imm8: 66 0F 70 /r ib
			# SHUFPS  xmm, xmm/m128, imm8: 0F C6 /r ib
			# SHUFPD  xmm, xmm/m128, imm8: 66 0F C6 /r ib

			if name == 'SHUFPS':
				self.size = 3 + 1 + source.get_modrm_extra_length()
			else:
				self.size = 1 + 3 + 1 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.immediate)

	def get_input_registers_list(self):
		input_registers_list = self.source.get_registers_list()
		if self.name in ['SHUFPS', 'SHUFPD', 'PSHUFLW', 'PSHUFHW']:
			input_registers_list += self.destination.get_registers_list()
		return input_registers_list

	def get_output_registers_list(self):
		return self.destination.get_registers_list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class MmxSseAlignInstruction(Instruction):
	def __init__(self, destination, source, immediate, origin = None):
		super(MmxSseAlignInstruction, self).__init__('PALIGNR', isa_extension = "SSSE3", origin = origin)
		self.destination = destination
		self.source = source
		self.immediate = immediate
		if destination.is_mmx_register() and (source.is_mmx_register() or source.is_memory_address64()) and immediate.is_uint8():
			# PALIGNR mm, mm/m64, imm8: 0F 3A 0F /r ib

			self.size = 4 + source.get_modrm_extra_length() + 1
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()) and immediate.is_uint8():
			# PALIGNR xmm, xmm/m128, imm8: 66 0F 3A 0F /r ib

			self.size = 1 + 4 + source.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(self.name, destination, source, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.immediate)

	def get_input_registers_list(self):
		return self.source.get_registers_list() + self.destination.get_registers_list()

	def get_output_registers_list(self):
		return self.destination.get_registers_list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseOctowordShiftInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		shift_instructions = ['PSLLDQ', 'PSRLDQ']
		if name in shift_instructions:
			super(SseOctowordShiftInstruction, self).__init__(name, destination, source, isa_extension = "SSE2", origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the octoword shift instructions ({1})'.format(name, ", ".join(shift_instructions)))
		if destination.is_sse_register() and source.is_int8():
			# PSLLDQ xmm, imm8: 66 0F 73 /7 ib
			# PSRLDQ xmm, imm8: 66 0F 73 /3 ib
			self.size = 4 + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class SseMovExtendInstruction(BinaryInstruction):
	def __init__(self, name, destination, source, origin = None):
		m16_loads = [ 'PMOVSXBQ', 'PMOVZXBQ' ]
		m32_loads = [ 'PMOVSXBD', 'PMOVZXBD', 'PMOVSXWQ', 'PMOVZXWQ' ]
		m64_loads = [ 'PMOVSXBW', 'PMOVZXBW', 'PMOVSXWD', 'PMOVZXWD', 'PMOVSXDQ', 'PMOVZXDQ' ]
		mov_extend_instructions = m16_loads + m32_loads + m64_loads
		if name in mov_extend_instructions:
			super(SseMovExtendInstruction, self).__init__(name, destination, source, isa_extension = 'SSE4.1', origin = origin)
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

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxMovExtendInstruction(Instruction):
	def __init__(self, name, destination, source, origin = None):
		m16_loads = [ 'VPMOVSXBQ', 'VPMOVZXBQ' ]
		m32_loads = [ 'VPMOVSXBD', 'VPMOVZXBD', 'VPMOVSXWQ', 'VPMOVZXWQ' ]
		m64_loads = [ 'VPMOVSXBW', 'VPMOVZXBW', 'VPMOVSXWD', 'VPMOVZXWD', 'VPMOVSXDQ', 'VPMOVZXDQ' ]
		mov_extend_instructions = m16_loads + m32_loads + m64_loads
		if name not in mov_extend_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})', name, ", ".join(mov_extend_instructions))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address16()) and name in m16_loads:
			# VPMOVSXBQ xmm, xmm/m16: VEX.128.66.0F38.WIG 22 /r
			# VPMOVZXBQ xmm, xmm/m16: VEX.128.66.0F38.WIG 32 /r
			super(AvxMovExtendInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_avx_register() and (source.is_sse_register() or source.is_memory_address32()) and name in m16_loads:
			# VPMOVSXBQ ymm, xmm/m32: VEX.256.66.0F38.WIG 22 /r
			# VPMOVZXBQ ymm, xmm/m32: VEX.256.66.0F38.WIG 32 /r
			super(AvxMovExtendInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address32()) and name in m32_loads:
			# VPMOVSXBD xmm, xmm/m32: VEX.128.66.0F38.WIG 21 /r
			# VPMOVZXBD xmm, xmm/m32: VEX.128.66.0F38.WIG 31 /r
			# VPMOVSXWQ xmm, xmm/m32: VEX.128.66.0F38.WIG 24 /r
			# VPMOVZXWQ xmm, xmm/m32: VEX.128.66.0F38.WIG 34 /r
			super(AvxMovExtendInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_avx_register() and (source.is_sse_register() or source.is_memory_address64()) and name in m32_loads:
			# VPMOVSXBD ymm, xmm/m64: VEX.256.66.0F38.WIG 21 /r
			# VPMOVZXBD ymm, xmm/m64: VEX.256.66.0F38.WIG 31 /r
			# VPMOVSXWQ ymm, xmm/m64: VEX.256.66.0F38.WIG 24 /r
			# VPMOVZXWQ ymm, xmm/m64: VEX.256.66.0F38.WIG 34 /r
			super(AvxMovExtendInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address64()) and name in m64_loads:
			# VPMOVSXBW xmm, xmm/m64: VEX.128.66.0F38.WIG 20 /r
			# VPMOVZXBW xmm, xmm/m64: VEX.128.66.0F38.WIG 30 /r
			# VPMOVSXWD xmm, xmm/m64: VEX.128.66.0F38.WIG 23 /r
			# VPMOVZXWD xmm, xmm/m64: VEX.128.66.0F38.WIG 33 /r
			# VPMOVSXDQ xmm, xmm/m64: VEX.128.66.0F38.WIG 25 /r
			# VPMOVZXDQ xmm, xmm/m64: VEx.128.66.0F38.WIG 35 /r
			super(AvxMovExtendInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		elif destination.is_avx_register() and (source.is_sse_register() or source.is_memory_address128()) and name in m64_loads:
			# VPMOVSXBW ymm, xmm/m128: VEX.256.66.0F38.WIG 20 /r
			# VPMOVZXBW ymm, xmm/m128: VEX.256.66.0F38.WIG 30 /r
			# VPMOVSXWD ymm, xmm/m128: VEX.256.66.0F38.WIG 23 /r
			# VPMOVZXWD ymm, xmm/m128: VEX.256.66.0F38.WIG 33 /r
			# VPMOVSXDQ ymm, xmm/m128: VEX.256.66.0F38.WIG 25 /r
			# VPMOVZXDQ ymm, xmm/m128: VEx.256.66.0F38.WIG 35 /r
			super(AvxMovExtendInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source = source
			self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}'.format(name, destination, source))

	def __str__(self):
		return "{0} {1}, {2}".format(self.name, self.destination, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class SseBlendMaskedInstruction(Instruction):
	def __init__(self, name, destination, source, mask, origin = None):
		allowed_instructions = ['BLENDVPS', 'BLENDVPD', 'PBLENDVB']
		if name in allowed_instructions:
			super(SseBlendMaskedInstruction, self).__init__(name, isa_extension = 'SSE4.1', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and (source.is_sse_register() or source.is_memory_address128()) and (mask.is_sse_register() and (mask.register.is_virtual() or mask.register == xmm0)):
			# BLENDVPS xmm, xmm/m128: 66 0F 38 14 /r
			# BLENDVPD xmm, xmm/m128: 66 0F 38 15 /r
			# PBLENDVB xmm, xmm/m128: 66 0F 38 10 /r

			self.destination = destination
			self.source = source
			self.mask = mask
			self.size = 5 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}'.format(name, destination, source, mask))

	def __str__(self):
		return "{0} {1}, {2}, {3}".format(self.name, self.destination, self.source, self.mask)

	def get_input_registers_list(self):
		return self.destination.get_registers_list() + self.source.get_registers_list() + self.mask.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class AvxBlendMaskedInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, mask, origin = None):
		allowed_instructions = ['VBLENDVPS', 'VBLENDVPD', 'VPBLENDVB']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()) and mask.is_sse_register():
			# VBLENDVPS xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 4A /r /is4
			# VBLENDVPD xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 4B /r /is4
			# VPBLENDVB xmm, xmm, xmm/m128, xmm: VEX.NDS.128.66.0F3A.W0 4C /r /is4

			super(AvxBlendMaskedInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.mask = mask
			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		elif name in ['VBLENDVPS', 'VBLENDVPD'] and destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) and mask.is_avx_register():
			# VBLENDVPS ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 4A /r /is4
			# VBLENDVPD ymm, ymm, ymm/m256, ymm: VEX.NDS.256.66.0F3A.W0 4B /r /is4

			super(AvxBlendMaskedInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.mask = mask
			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		elif name == 'VPBLENDVB' and destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) and mask.is_avx_register():
			# VPBLENDVB ymm, ymm, ymm/m256, xmm: VEX.NDS.256.66.0F3A.W0 4C /r /is4

			super(AvxBlendMaskedInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.mask = mask
			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}'.format(name, destination, source_x, source_y, mask))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}".format(self.name, self.destination, self.source_x, self.source_y, self.mask)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list() + self.mask.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class AvxBlendInstruction(Instruction):
	def __init__(self, name, destination, source_x, source_y, immediate, origin = None):
		allowed_instructions = ['VBLENDPS', 'VBLENDPD', 'VPBLENDW', 'VPBLENDD']
		if name not in allowed_instructions:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(allowed_instructions)))
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()) and immediate.is_uint8():
			# VBLENDPS xmm, xmm, xmm/m128, imm8: VEX.NDS.128.66.0F3A.WIG 0C /r ib
			# VBLENDPD xmm, xmm, xmm/m128, imm8: VEX.NDS.128.66.0F3A.WIG 0D /r ib
			# VPBLENDW xmm, xmm, xmm/m128, imm8: VEX.NDS.128.66.0F3A.WIG 0E /r ib
			# VPBLENDD xmm, xmm, xmm/m128, imm8: VEX.NDS.128.66.0F3A.WIG 02 /r ib
			
			if name == 'VPBLENDD':
				super(AvxBlendInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			else:
				super(AvxBlendInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.immediate = immediate
			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) and immediate.is_uint8():
			# VBLENDPS ymm, ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.WIG 0C /r ib
			# VBLENDPD ymm, ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.WIG 0D /r ib
			# VPBLENDW ymm, ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.WIG 0E /r ib
			# VPBLENDD ymm, ymm, ymm/m256, imm8: VEX.NDS.256.66.0F3A.WIG 02 /r ib

			if name in ('VPBLENDW', 'VPBLENDD'):
				super(AvxBlendInstruction, self).__init__(name, isa_extension = 'AVX2', origin = origin)
			else:
				super(AvxBlendInstruction, self).__init__(name, isa_extension = 'AVX', origin = origin)
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.immediate = immediate
			self.size = source_y.get_vex_extra_length() + 1 + source_y.get_modrm_extra_length() + 1
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}'.format(name, destination, source_x, source_y, immediate))

	def __str__(self):
		return "{0} {1}, {2}, {3}, {4}".format(self.name, self.destination, self.source_x, self.source_y, self.immediate)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		else:
			return None

class XopConditionalMoveInstruction(Instruction):
	def __init__(self, destination, source_x, source_y, source_z, origin = None):
		super(XopConditionalMoveInstruction, self).__init__('VPCMOV', isa_extension = 'XOP', origin = origin)
		if destination.is_sse_register() and source_x.is_sse_register() and (source_y.is_sse_register() or source_y.is_memory_address128()) and source_z.is_sse_register():
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.source_z = source_z

			self.size = 4 + source_y.get_modrm_extra_length()
		elif destination.is_sse_register() and source_x.is_sse_register() and source_y.is_sse_register() and (source_z.is_sse_register() or source_z.is_memory_address128()):
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.source_z = source_z

			self.size = 4 + source_y.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and (source_y.is_avx_register() or source_y.is_memory_address256()) and source_z.is_avx_register():
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.source_z = source_z

			self.size = 4 + source_y.get_modrm_extra_length()
		elif destination.is_avx_register() and source_x.is_avx_register() and source_y.is_avx_register() and (source_z.is_avx_register() or source_z.is_memory_address256()):
			self.destination = destination
			self.source_x = source_x
			self.source_y = source_y
			self.source_z = source_z

			self.size = 4 + source_y.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}, {2}, {3}, {4}'.format(self.name, destination, source_x, source_y, source_z))

	def __str__(self):
		return "VPCMOV {0}, {1}, {2}, {3}".format(self.destination, self.source_x, self.source_y, self.source_z)

	def get_input_registers_list(self):
		return self.source_x.get_registers_list() + self.source_y.get_registers_list() + self.source_z.get_registers_list()

	def get_output_registers_list(self):
		return [self.destination.register]

	def get_constant(self):
		if self.source_y.is_constant():
			return self.source_y.constant
		elif self.source_z.is_constant():
			return self.source_z.constant
		else:
			return None

	def get_local_variable(self):
		if self.source_y.is_local_variable():
			return self.source_y.variable
		elif self.source_z.is_local_variable():
			return self.source_z.variable
		else:
			return None

class PrefetchInstruction(Instruction):
	def __init__(self, name, source, origin = None):
		sse_prefetch_instructions = ['PREFETCHT0', 'PREFETCHT1', 'PREFETCHT2', 'PREFETCHNTA']
		k3d_prefetch_instructions = ['PREFETCH', 'PREFETCHW']
		prefetch_instructions = sse_prefetch_instructions + k3d_prefetch_instructions
		if name in sse_prefetch_instructions:
			super(PrefetchInstruction, self).__init__(name, isa_extension = 'SSE', origin = origin)
		elif name in k3d_prefetch_instructions:
			super(PrefetchInstruction, self).__init__(name, isa_extension = '3dnow! Prefetch', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(prefetch_instructions)))
		if source.is_memory_address():
			# PREFETCHNTA m8: 0F 18 /0
			#  PREFETCHT0 m8: 0F 18 /1
			#  PREFETCHT1 m8: 0F 18 /2
			#  PREFETCHT2 m8: 0F 18 /3
			#    PREFETCH m8: 0F 0D /0
			#   PREFETCHW m8: 0F 0D /1

			self.source = source
			self.size = 3 + source.get_modrm_extra_length()
		else:
			raise ValueError('Invalid operands in instruction {0} {1}'.format(self.name, source))

	def __str__(self):
		return "{0} {1}".format(self.name, self.source)

	def get_input_registers_list(self):
		return self.source.get_registers_list()

	def get_output_registers_list(self):
		return list()

	def get_constant(self):
		if self.source.is_constant():
			return self.source.constant
		else:
			return None

	def get_local_variable(self):
		if self.source.is_local_variable():
			return self.source.variable
		else:
			return None

class FenceInstruction(Instruction):
	def __init__(self, name, origin = None):
		sse_instructions   = ['SFENCE']
		sse2_instructions  = ['LFENCE', 'MFENCE']
		fence_instructions = sse_instructions + sse2_instructions
		if name in sse_instructions:
			super(FenceInstruction, self).__init__(name, isa_extension = 'SSE', origin = origin)
		elif name in sse2_instructions:
			super(FenceInstruction, self).__init__(name, isa_extension = 'SSE2', origin = origin)
		else:
			raise ValueError('Instruction {0} is not one of the allowed instructions ({1})'.format(name, ", ".join(fence_instructions)))
		# LFENCE: 0F AE /5
		# MFENCE: 0F AE /6
		# SFENCE: 0F AE /7

		self.size = 3

	def get_input_registers_list(self):
		return list()

	def get_output_registers_list(self):
		return list()

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class JmpInstruction(Instruction):
	def __init__(self, destination, origin = None):
		super(JmpInstruction, self).__init__("JMP", origin = origin)
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

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class PushInstruction(Instruction):
	def __init__(self, source, origin = None):
		super(PushInstruction, self).__init__('PUSH', origin = origin)
		self.source = source
		if source.is_general_purpose_register64():
			self.size = 1 + 1
		else:
			raise ValueError('Invalid operand in instruction PUSH {0}'.format(source))

	def __str__(self):
		return "PUSH {0}".format(self.source)

	def get_input_registers_list(self):
		input_registers_list = [rsp]
		input_registers_list.extend(self.source.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		return [rsp]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class PopInstruction(Instruction):
	def __init__(self, destination, origin = None):
		super(PopInstruction, self).__init__('POP', origin = origin)
		self.destination = destination
		if destination.is_general_purpose_register64():
			self.size = 1 + 1
		else:
			raise ValueError('Invalid operand in instruction POP {0}'.format(destination))

	def __str__(self):
		return "POP {0}".format(self.destination)

	def get_input_registers_list(self):
		input_registers_list = [rsp]
		if self.destination.is_memory_address():
			input_registers_list.extend(self.destination.get_registers_list())
		return input_registers_list

	def get_output_registers_list(self):
		output_registers_list = [rsp]
		if self.destination.is_register():
			output_registers_list.append(self.destination.register)
		return output_registers_list

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class RetInstruction(Instruction):
	def __init__(self, frame_size, origin = None):
		super(RetInstruction, self).__init__('RET', origin = origin)
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
		return [rsp]

	def get_output_registers_list(self):
		return [rsp]

	def get_constant(self):
		return None

	def get_local_variable(self):
		return None

class ReturnInstruction(QuasiInstruction):
	def __init__(self, return_value = None, origin = None):
		super(ReturnInstruction, self).__init__('RETURN', origin = origin)
		if return_value.is_none():
			self.return_value = None
		elif return_value.is_int32():
			self.return_value = return_value.immediate
		else:
			raise ValueError('Return value is not a 32-bit integer')

	def to_instruction_list(self):
		instruction_list = list()
		if self.return_value is None:
			pass
		elif self.return_value == 0:
			instruction_list.append(ArithmeticInstruction('XOR', Operand(eax), Operand(eax)))
		else:
			instruction_list.append(MovInstruction(Operand(eax), Operand(self.return_value)))
		instruction_list.append(RetInstruction(Operand(None)))
		return instruction_list

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

class Int3Instruction(Instruction):
	def __init__(self, origin = None):
		super(Int3Instruction, self).__init__('INT', origin = origin)
		# INT 3: CC
		self.size = 1

	def __str__(self):
		return "INT 3"

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

def INT3():
	instruction = Int3Instruction()
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
			if argument.get_type().is_pointer() or argument.get_type().is_integer():
				register = GeneralPurposeRegister64()
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
			if isinstance(destination, MMXRegister):
				PXOR( destination, destination )
			elif isinstance(destination, SSERegister):
				if ctype.is_floating_point():
					if Target.has_avx():
						SIMD_XOR = {4: VXORPS, 8: VXORPD }[ctype.get_size()]
					else:
						SIMD_XOR = {4: XORPS, 8: XORPD}[ctype.get_size()]
				else:
					SIMD_XOR = VPXOR if Target.has_avx() else PXOR
				SIMD_XOR( destination, destination )
			elif isinstance(destination, AVXRegister):
				LOAD.ZERO( destination.get_oword(), ctype )
			else:
				raise TypeError("Unsupported type of destination register")
		else:
			raise TypeError("Type must be a C type")

	@staticmethod
	def ELEMENT(destination, source, ctype, increment_pointer = False):
		if isinstance(ctype, peachpy.c.Type):
			if Operand(destination).is_register():
				if Operand(source).is_memory_address():
					memory_size = ctype.get_size(current_function.abi)
					source_address = source[0]
					if isinstance(destination, GeneralPurposeRegister64):
						if ctype.is_unsigned_integer() or ctype.is_pointer():
							if memory_size == 8:
								MOV( destination, source )
							elif memory_size == 4:
								MOV( destination.get_dword(), source )
							elif memory_size == 2:
								MOVZX( destination.get_dword(), word[source_address] )
							elif memory_size == 1:
								MOVZX( destination.get_dword(), byte[source_address] )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						elif ctype.is_signed_integer():
							if memory_size == 8:
								MOV( destination, source )
							elif memory_size == 4:
								MOVSX( destination, dword[source_address] )
							elif memory_size == 2:
								MOVSX( destination, word[source_address] )
							elif memory_size == 1:
								MOVSX( destination, byte[source_address] )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, GeneralPurposeRegister32):
						if ctype.is_unsigned_integer():
							if memory_size == 4:
								MOV( destination, source )
							elif memory_size == 2:
								MOVZX( destination, word[source_address] )
							elif memory_size == 1:
								MOVZX( destination, byte[source_address] )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						elif ctype.is_signed_integer():
							if memory_size == 4:
								MOV( destination, source )
							elif memory_size == 2:
								MOVSX( destination, word[source_address] )
							elif memory_size == 1:
								MOVSX( destination, byte[source_address] )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, GeneralPurposeRegister16):
						if ctype.is_unsigned_integer():
							if memory_size == 2:
								MOV( destination, source )
							elif memory_size == 1:
								MOVZX( destination, byte[source_address] )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						elif ctype.is_signed_integer():
							if memory_size == 2:
								MOV( destination, source )
							elif memory_size == 1:
								MOVSX( destination, byte[source_address] )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, GeneralPurposeRegister8):
						if ctype.is_integer():
							if memory_size == 1:
								MOV( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, SSERegister):
						if ctype.is_floating_point():
							if memory_size == 4:
								if Target.has_avx():
									VMOVSS( destination, source )
								else:
									MOVSS( destination, source )
							elif memory_size == 8:
								if Target.has_avx():
									VMOVSD( destination, source )
								else:
									MOVSD( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(destination, AVXRegister):
						if ctype.is_floating_point():
							if memory_size == 4:
								VMOVSS( destination.get_oword(), source )
							elif memory_size == 8:
								VMOVSD( destination.get_oword(), source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					else:
						raise TypeError("Destination must be a general-purpose register")
					if increment_pointer:
						ADD( source_address, memory_size )
				else:
					raise TypeError("Source must be a memory operand")
			else:
				raise TypeError("Destination must be a register")
		else:
			raise TypeError("Type must be a C type")

class BROADCAST:
	@staticmethod
	def ELEMENT(destination, source, input_type, output_type = None):
		if output_type is None:
			output_type = input_type
		if isinstance(input_type, peachpy.c.Type) and isinstance(output_type, peachpy.c.Type):
			if input_type.is_integer():
				if not output_type.is_integer():
					raise TypeError("Mismatch between input and output types")
				if input_type.is_unsigned_integer() and not output_type.is_unsigned_integer():
					raise TypeError("Mismatch between input and output types")
				if input_type.is_signed_integer() and not output_type.is_signed_integer():
					raise TypeError("Mismatch between input and output types")
				if input_type.get_size() > output_type.get_size():
					raise TypeError("Input type is wider than output type")

				if isinstance(destination, SSERegister) and input_type.get_size() == 1:
					if isinstance(source, GeneralPurposeRegister8):
						pass 
					elif isinstance(source, GeneralPurposeRegister):
						source = source.get_low_byte() 
					else:
						raise TypeError("Invalid source operand {0}".format(source))
					if output_type.get_size() == 1:
						temp = GeneralPurposeRegister32()
						MOVZX( temp, source )
						IMUL( temp, temp, 0x01010101 )
						MOVD( destination, temp )
						PSHUFD( destination, destination, 0x00 )
					elif output_type.get_size() == 2:
						temp = GeneralPurposeRegister32()
						if output_type.is_signed_integer():
							MOVSX( temp.get_word(), source )
							source = temp.get_word()
						MOVZX( temp, source )
						IMUL( temp, temp, 0x00010001 )
						MOVD( destination, temp )
						PSHUFD( destination, destination, 0x00 )
					elif output_type.get_size() == 4:
						temp = GeneralPurposeRegister32()
						if output_type.is_signed_integer():
							MOVSX( temp, source )
						else:
							MOVZX( temp, source )
						MOVD( destination, temp )
						PSHUFD( destination, destination, 0x00 )
					elif output_type.get_size() == 8:
						if output_type.is_signed_integer():
							temp = GeneralPurposeRegister64()
							MOVSX( temp, source )
							MOVQ( destination, temp )
						else:
							temp = GeneralPurposeRegister32()
							MOVZX( temp, source )
							MOVD( destination, temp )
						PUNPCKLQDQ( destination, destination )
					else:
						raise TypeError("Unsupported output type {0}".format(output_type))
				elif isinstance(destination, SSERegister) and input_type.get_size() == 2:
					if isinstance(source, GeneralPurposeRegister16):
						pass
					elif isinstance(source, GeneralPurposeRegister32) or isinstance(source, GeneralPurposeRegister64):
						source = source.get_word()
					else:
						raise TypeError("Invalid source operand {0}".format(source))
					if output_type.get_size() == 2:
						temp = GeneralPurposeRegister32()
						MOVZX( temp, source )
						IMUL( temp, temp, 0x00010001 )
						MOVD( destination, temp )
						PSHUFD( destination, destination, 0x00 )
					elif output_type.get_size() == 4:
						temp = GeneralPurposeRegister32()
						if output_type.is_signed_integer():
							MOVSX( temp, source )
						else:
							MOVZX( temp, source )
						MOVD( destination, temp )
						PSHUFD( destination, destination, 0x00 )
					elif output_type.get_size() == 8:
						if output_type.is_signed_integer():
							temp = GeneralPurposeRegister64()
							MOVSX( temp, source )
							MOVQ( destination, temp )
						else:
							temp = GeneralPurposeRegister32()
							MOVZX( temp, source )
							MOVD( destination, temp )
						PUNPCKLQDQ( destination, destination )
					else:
						raise TypeError("Unsupported output type {0}".format(output_type))
				elif isinstance(destination, SSERegister) and input_type.get_size() == 4:
					if isinstance(source, GeneralPurposeRegister32):
						pass
					elif isinstance(source, GeneralPurposeRegister64):
						source = source.get_dword()
					else:
						raise TypeError("Invalid source operand {0}".format(source))
					if output_type.get_size() == 4:
						MOVD( destination, source )
						PSHUFD( destination, destination, 0x00 )
					elif output_type.get_size() == 8:
						if output_type.is_signed_integer():
							temp = GeneralPurposeRegister64()
							MOVSX( temp, source )
							MOVQ( destination, temp )
						else:
							MOVD( destination, source )
						PUNPCKLQDQ( destination, destination )
					else:
						raise TypeError("Unsupported output type {0}".format(output_type))
				elif isinstance(destination, SSERegister) and input_type.get_size() == 8:
					if isinstance(source, GeneralPurposeRegister64):
						pass
					else:
						raise TypeError("Invalid source operand {0}".format(source))
					if output_type.get_size() == 8:
						MOVQ( destination, source )
						PUNPCKLQDQ( destination, destination )
					else:
						raise TypeError("Unsupported output type {0}".format(output_type))
				else:
					raise TypeError("Source must be a memory operand")
			else:
				raise TypeError("Unsupported input type {0}".format(input_type))
		else:
			raise TypeError("Input and output types must be C types")

class STORE:
	@staticmethod
	def ELEMENT(destination, source, ctype, increment_pointer = False):
		if isinstance(ctype, peachpy.c.Type):
			if Operand(destination).is_memory_address():
				if Operand(source).is_register():
					memory_size = ctype.get_size(current_function.abi)
					if isinstance(source, GeneralPurposeRegister64):
						if ctype.is_integer():
							if memory_size == 8:
								MOV( destination, source )
							elif memory_size == 4:
								MOV( destination, source.get_dword() )
							elif memory_size == 2:
								MOV( destination, source.get_word() )
							elif memory_size == 1:
								MOV( destination, source.get_low_byte() )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						elif ctype.is_pointer():
							if memory_size == 8:
								MOV( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, GeneralPurposeRegister32):
						if ctype.is_integer():
							if memory_size == 4:
								MOV( destination, source )
							elif memory_size == 2:
								MOV( destination, source.get_word() )
							elif memory_size == 1:
								MOV( destination, source.get_low_byte() )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, GeneralPurposeRegister16):
						if ctype.is_integer():
							if memory_size == 2:
								MOV( destination, source )
							elif memory_size == 1:
								MOV( destination, source.get_low_byte() )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, GeneralPurposeRegister8):
						if ctype.is_integer():
							if memory_size == 1:
								MOV( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, SSERegister):
						if ctype.is_floating_point():
							if memory_size == 4:
								if Target.has_avx():
									VMOVSS( destination, source )
								else:
									MOVSS( destination, source )
							elif memory_size == 8:
								if Target.has_avx():
									VMOVSD( destination, source )
								else:
									MOVSD( destination, source )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					elif isinstance(source, AVXRegister):
						if ctype.is_floating_point():
							if memory_size == 4:
								VMOVSS( destination, source.get_oword() )
							elif memory_size == 8:
								VMOVSD( destination, source.get_oword() )
							else:
								raise ValueError("Invalid memory operand size {0}".format(memory_size))
						else:
							raise TypeError("Invalid memory operand type")
					else:
						raise TypeError("Source must be a general-purpose register")
					if increment_pointer:
						destination_address = destination[0]
						ADD( destination_address, memory_size )
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
					if Target.has_avx():
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

class CMP(object):
	@staticmethod
	def __new__(cls, destination, source):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		instruction = ArithmeticInstruction('CMP', Operand(destination), Operand(source), origin = origin)
		if current_stream is not None:
			current_stream.add_instruction(instruction)
		return instruction

	@staticmethod
	def JA(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JA(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JAE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JAE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JB(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JB(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JBE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JBE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JC(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JC(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JG(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JG(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JGE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JGE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JL(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JL(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JLE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JLE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JO(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JO(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JP(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JP(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JPO(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JPO(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JS(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JS(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JZ(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JZ(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNA(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNA(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNAE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNAE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNB(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNB(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNBE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNBE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNC(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNC(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNG(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNG(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNGE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNGE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNL(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNL(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNLE(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNLE(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNO(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNO(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNP(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNP(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNPO(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNPO(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNS(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNS(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction
	
	@staticmethod
	def JNZ(source_x, source_y, label):
		origin = inspect.stack() if Function.get_current().collect_origin else None
		with InstructionStream():
			instruction = CompareAndBranchInstruction(CMP(source_x, source_y), JNZ(label), origin = origin)
		if current_stream:
			current_stream.add_instruction(instruction)
		return instruction

def EMMS():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxClearStateInstruction('EMMS', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def FEMMS():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxClearStateInstruction('FEMMS', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VZEROALL():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxZeroInstruction('VZEROALL', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VZEROUPPER():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxZeroInstruction('VZEROUPPER', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def ADD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('ADD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('ADC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('SUB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SBB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('SBB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AND(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('AND', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def OR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('OR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def XOR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('XOR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TEST(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ArithmeticInstruction('TEST', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def INC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryArithmeticInstruction('INC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def DEC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryArithmeticInstruction('DEC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def NOT(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryArithmeticInstruction('NOT', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def NEG(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryArithmeticInstruction('NEG', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SHL(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('SHL', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SHR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('SHR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SAR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('SAR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ROL(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('ROL', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ROR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('ROR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RCL(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('RCL', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RCR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ShiftInstruction('RCR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LEA(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = LoadAddressInstruction(Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BT(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BitTestInstruction('BT', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BTS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BitTestInstruction('BTS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BTR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BitTestInstruction('BTR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BTC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BitTestInstruction('BTC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def IMUL(destination = None, source = None, immediate = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ImulInstruction(Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MUL(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MulInstruction(Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RET(immediate = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = RetInstruction(Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOV(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MovInstruction(Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVZX(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MoveExtendInstruction('MOVZX', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVSX(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MoveExtendInstruction('MOVSX', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BSWAP(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ByteSwapInstruction(Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def POPCNT(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitCountInstruction('POPCNT', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LZCNT(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitCountInstruction('LZCNT', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def TZCNT(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitCountInstruction('TZCNT', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BSF(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitCountInstruction('BSF', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BSR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitCountInstruction('BSR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CRC32(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CRC32Instruction(Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLSI(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitManipulationInstruction('BLSI', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLSMSK(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitManipulationInstruction('BLSMSK', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLSR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = UnaryBitManipulationInstruction('BLSR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDN(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('ANDN', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BEXR(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('BEXR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BZHI(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('BZHI', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MULX(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('MULX', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PDEP(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('PDEP', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PEXT(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('PEXT', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SARX(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('SARX', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SHRX(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('SHRX', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SHLX(destination, source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BinaryBitManipulationInstruction('SHLX', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def RORX(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = BmiRotateInstruction(Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUSH(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PushInstruction(Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def POP(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PopInstruction(Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVA(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVA', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVAE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVAE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVBE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVBE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVG(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVG', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVGE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVGE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVL(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVL', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVLE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVLE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVO(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVO', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVPO(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVPO', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVZ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVZ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNA(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNA', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNAE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNAE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNBE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNBE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNG(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNG', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNGE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNGE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNL(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNL', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNLE(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNLE', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNO(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNO', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNPO(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNPO', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMOVNZ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = CmovInstruction('CMOVNZ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETA(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETA', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETAE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETAE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETB(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETB', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETBE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETBE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETG(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETG', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETGE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETGE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETL(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETL', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETLE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETLE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETP(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETP', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETPO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETPO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETZ(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETZ', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNA(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNA', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNAE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNAE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNB(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNB', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNBE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNBE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNG(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNG', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNGE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNGE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNL(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNL', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNLE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNLE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNP(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNP', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNPO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNPO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SETNZ(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SetInstruction('SETNZ', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JA(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JA', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JAE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JAE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JB(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JB', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JBE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JBE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JG(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JG', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JGE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JGE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JL(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JL', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JLE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JLE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JP(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JP', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JPO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JPO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JZ(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JZ', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNA(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNA', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNAE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNAE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNB(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNB', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNBE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNBE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNC(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNC', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNG(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNG', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNGE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNGE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNL(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNL', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNLE(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNLE', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNP(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNP', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNPO(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNPO', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNS(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNS', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JNZ(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = ConditionalJumpInstruction('JNZ', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def JMP(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = JmpInstruction(Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PREFETCH(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PrefetchInstruction('PREFETCH', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
	
def PREFETCHW(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PrefetchInstruction('PREFETCHW', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PREFETCHT0(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PrefetchInstruction('PREFETCHT0', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PREFETCHT1(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PrefetchInstruction('PREFETCHT1', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PREFETCHT2(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PrefetchInstruction('PREFETCHT2', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PREFETCHNTA(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = PrefetchInstruction('PREFETCHNTA', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SFENCE():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = FenceInstruction('SFENCE', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LFENCE():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = FenceInstruction('LFENCE', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MFENCE():
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = FenceInstruction('MFENCE', origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseMovWordInstruction('MOVD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseMovWordInstruction('MOVQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVAPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovInstruction('MOVAPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVUPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovInstruction('MOVUPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVAPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovInstruction('MOVAPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVUPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovInstruction('MOVUPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVDQA(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovInstruction('MOVDQA', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVDQU(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovInstruction('MOVDQU', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLHPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseCrossMovHalfInstruction('MOVLHPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVHLPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseCrossMovHalfInstruction('MOVHLPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovHalfInstruction('MOVLPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVHPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovHalfInstruction('MOVHPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVLPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovHalfInstruction('MOVLPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVHPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovHalfInstruction('MOVHPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseScalarFloatingPointMovInstruction('MOVSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseScalarFloatingPointMovInstruction('MOVSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ADDSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ADDPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ADDSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ADDPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('SUBSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('SUBPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('SUBSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SUBPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('SUBPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MULSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MULSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MULPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MULPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MULSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MULSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MULPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MULPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def DIVSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('DIVSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def DIVPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('DIVPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def DIVSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('DIVSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def DIVPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('DIVPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPEQSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPEQSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLTSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLTSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLESS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLESS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPUNORDSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPUNORDSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNEQSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNEQSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLTSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLTSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLESS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLESS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPORDSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPORDSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPEQPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPEQPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLTPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLTPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLEPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLEPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPUNORDPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPUNORDPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNEQPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNEQPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLTPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLTPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLEPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLEPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPORDPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPORDPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPEQSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPEQSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLTSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLTSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLESD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLESD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPUNORDSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPUNORDSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNEQSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNEQSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLTSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLTSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLESD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLESD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPORDSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPORDSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPEQPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPEQPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLTPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLTPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPLEPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPLEPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPUNORDPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPUNORDPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNEQPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNEQPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLTPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLTPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPNLEPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPNLEPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CMPORDPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('CMPORDPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MINSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MINSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MINPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MINPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MINSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MINSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MINPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MINPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MAXSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MAXSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MAXPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MAXPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MAXSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MAXSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MAXPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('MAXPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def HADDPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('HADDPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def HADDPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('HADDPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def HSUBPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('HSUBPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def HSUBPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('HSUBPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSUBPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ADDSUBPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ADDSUBPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ADDSUBPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ANDPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ANDPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDNPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ANDNPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ANDNPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ANDNPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ORPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def ORPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('ORPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def XORPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('XORPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def XORPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('XORPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def UNPCKLPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('UNPCKLPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def UNPCKLPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('UNPCKLPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def UNPCKHPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('UNPCKHPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def UNPCKHPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseFloatingPointBinaryInstruction('UNPCKHPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def LDMXCSR(source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MxcsrControlInstruction('LDMXCSR', Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def STMXCSR(destination):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MxcsrControlInstruction('STMXCSR', Operand(destination), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDUSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDUSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PADDUSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PADDUSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBUSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBUSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSUBUSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSUBUSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSLLW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSLLW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSLLD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSLLD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSLLQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSLLQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSRLW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSRLW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSRLD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSRLD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSRLQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSRLQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSRAW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSRAW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSRAD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSRAD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PAVGB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PAVGB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSLLDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSLLDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSRLDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShiftInstruction('PSRLDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PAVGW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PAVGW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMAXUB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMAXUB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMAXSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMAXSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMINUB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMINUB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMINSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMINSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSADBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSADBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PAND(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PAND', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PANDN(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PANDN', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def POR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('POR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PXOR(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PXOR', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPEQB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPEQB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPEQW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPEQW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPEQD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPEQD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPEQQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPEQQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPGTB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPGTB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPGTW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPGTW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPGTD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPGTD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PCMPGTQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PCMPGTQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULLD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULLD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULUDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULUDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULLW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULLW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULHW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULHW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULHUW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULHUW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMULHRSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMULHRSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMADDWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMADDWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMADDUBSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMADDUBSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKLBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKLBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKHBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKHBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKLWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKLWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKHWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKHWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKLDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKLDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKHDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKHDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKLQDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKLQDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PUNPCKHQDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PUNPCKHQDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSHUFW(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShuffleInstruction('PSHUFW', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSHUFLW(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShuffleInstruction('PSHUFLW', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSHUFHW(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShuffleInstruction('PSHUFHW', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSHUFD(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShuffleInstruction('PSHUFD', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SHUFPS(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShuffleInstruction('SHUFPS', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def SHUFPD(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseShuffleInstruction('SHUFPD', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PALIGNR(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseAlignInstruction(Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PACKSSWB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PACKSSWB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PACKSSDW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PACKSSDW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PACKUSWB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PACKUSWB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PACKUSDW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PACKUSDW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSIGNB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSIGNB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSIGNW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSIGNW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSIGND(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSIGND', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PABSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('PABSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PABSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('PABSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PABSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('PABSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHADDW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHADDW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHADDD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHADDD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHSUBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHSUBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHSUBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHSUBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHADDSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHADDSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHSUBSW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHSUBSW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PSHUFB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PSHUFB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PTEST(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PTEST', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMAXSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMAXSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMAXSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMAXSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMAXUW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMAXUW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMAXUD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMAXUD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMINSB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMINSB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMINSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMINSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMINUW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMINUW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMINUD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PMINUD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PHMINPOSUW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = MmxSseIntegerBinaryInstruction('PHMINPOSUW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLENDVPS(destination, source, mask):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseBlendMaskedInstruction('BLENDVPS', Operand(destination), Operand(source), Operand(mask), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def BLENDVPD(destination, source, mask):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseBlendMaskedInstruction('BLENDVPD', Operand(destination), Operand(source), Operand(mask), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PBLENDVB(destination, source, mask):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseBlendMaskedInstruction('PBLENDVB', Operand(destination), Operand(source), Operand(mask), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBLENDPS(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendInstruction('VBLENDPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBLENDPD(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendInstruction('VBLENDPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBLENDW(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendInstruction('VPBLENDW', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBLENDD(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendInstruction('VPBLENDD', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBLENDVPS(destination, source_x, source_y, mask):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendMaskedInstruction('VBLENDVPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(mask), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBLENDVPD(destination, source_x, source_y, mask):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendMaskedInstruction('VBLENDVPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(mask), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBLENDVB(destination, source_x, source_y, mask):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBlendMaskedInstruction('VPBLENDVB', Operand(destination), Operand(source_x), Operand(source_y), Operand(mask), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMOV(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopConditionalMoveInstruction(Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AESIMC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('AESIMC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AESENC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('AESENC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AESENCLAST(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('AESENCLAST', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AESDEC(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('AESDEC', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def AESDECLAST(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseIntegerUnaryInstruction('AESDECLAST', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVSXBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVSXBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVZXBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVZXBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVSXBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVSXBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVZXBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVZXBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVSXBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVSXBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVZXBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVZXBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVSXWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVSXWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVZXWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVZXWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVSXWQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVSXWQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVZXWQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVZXWQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVSXDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVSXDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def PMOVZXDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseMovExtendInstruction('PMOVZXDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVSXBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVSXBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVZXBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVZXBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVSXBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVSXBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVZXBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVZXBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVSXBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVSXBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVZXBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVZXBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVSXWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVSXWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVZXWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVZXWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVSXWQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVSXWQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVZXWQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVZXWQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVSXDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVSXDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMOVZXDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovExtendInstruction('VPMOVZXDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VEXTRACTF128(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxExtract128Instruction('VEXTRACTF128', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VEXTRACTI128(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxExtract128Instruction('VEXTRACTI128', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VINSERTF128(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxInsert128Instruction('VINSERTF128', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VINSERTI128(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxInsert128Instruction('VINSERTI128', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERM2F128(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxPermute128Instruction('VPERM2F128', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERM2I128(destination, source_x, source_y, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxPermute128Instruction('VPERM2I128', Operand(destination), Operand(source_x), Operand(source_y), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMILPS(destination, source, permutation):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxPermuteInstruction('VPERMILPS', Operand(destination), Operand(source), Operand(permutation), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMILPD(destination, source, permutation):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxPermuteInstruction('VPERMILPD', Operand(destination), Operand(source), Operand(permutation), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMIL2PS(destination, source_x, source_y, permutation, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopPermuteInstruction('VPERMIL2PS', Operand(destination), Operand(source_x), Operand(source_y), Operand(permutation), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMIL2PD(destination, source_x, source_y, permutation, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopPermuteInstruction('VPERMIL2PD', Operand(destination), Operand(source_x), Operand(source_y), Operand(permutation), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMPS(destination, source, permutation):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxCrossLanePermuteInstruction('VPERMPS', Operand(destination), Operand(source), Operand(permutation), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMPD(destination, source, permutation):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxCrossLanePermuteInstruction('VPERMPD', Operand(destination), Operand(source), Operand(permutation), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMD(destination, source, permutation):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxCrossLanePermuteInstruction('VPERMD', Operand(destination), Operand(source), Operand(permutation), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPERMQ(destination, source, permutation):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxCrossLanePermuteInstruction('VPERMQ', Operand(destination), Operand(source), Operand(permutation), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxScalarFloatingPointMovInstruction('VMOVSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxScalarFloatingPointMovInstruction('VMOVSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VADDSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VADDSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VADDSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VADDSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSUBSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VSUBSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSUBSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VSUBSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMAXSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VMAXSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMAXSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VMAXSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMINSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VMINSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMINSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VMINSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMULSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VMULSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMULSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VMULSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VDIVSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VDIVSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VDIVSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarBinaryInstruction('VDIVSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVAPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovInstruction('VMOVAPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVUPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovInstruction('VMOVUPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVAPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovInstruction('VMOVAPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVUPD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovInstruction('VMOVUPD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVDQA(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovInstruction('VMOVDQA', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVDQU(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovInstruction('VMOVDQU', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVLHPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxCrossMovHalfInstruction('VMOVLHPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVHLPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxCrossMovHalfInstruction('VMOVHLPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVLPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovHalfInstruction('VMOVLPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVHPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovHalfInstruction('VMOVHPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVLPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovHalfInstruction('VMOVLPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVHPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxMovHalfInstruction('VMOVHPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VADDPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VADDPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VADDPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VADDPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSUBPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VSUBPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VSUBPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VSUBPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMAXPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VMAXPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMAXPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VMAXPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMINPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VMINPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMINPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VMINPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMULPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VMULPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMULPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VMULPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VDIVPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VDIVPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VDIVPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VDIVPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VANDPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VANDPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VANDPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VANDPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VANDNPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VANDNPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VANDNPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VANDNPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VORPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VORPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VORPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VORPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VXORPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VXORPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VXORPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VXORPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VUNPCKLPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VUNPCKLPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VUNPCKLPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VUNPCKLPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VUNPCKHPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VUNPCKHPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VUNPCKHPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VUNPCKHPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VHADDPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VHADDPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VHADDPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VHADDPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VHSUBPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VHSUBPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VHSUBPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VHSUBPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VADDSUBPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VADDSUBPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VADDSUBPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointVectorBinaryInstruction('VADDSUBPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VROUNDPS(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxVectorRoundInstruction('VROUNDPS', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VROUNDPD(destination, source, immediate):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxVectorRoundInstruction('VROUNDPD', Operand(destination), Operand(source), Operand(immediate), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPEQPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPEQPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPEQPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPEQPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLTPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLTPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLTPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLTPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPGTPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPGTPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLEPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLEPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLEPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLEPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPUNORDPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPUNORDPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPUNORDPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPUNORDPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNEQPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNEQPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNEQPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNEQPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLTPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLTPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLTPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLTPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLEPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLEPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLEPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLEPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPORDPS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPORDPS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPORDPD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPORDPD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPEQSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPEQSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPEQSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPEQSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLTSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLTSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLTSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLTSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPGTSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPGTSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLESS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLESS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPLESD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPLESD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPUNORDSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPUNORDSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPUNORDSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPUNORDSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNEQSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNEQSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNEQSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNEQSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLTSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLTSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLTSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLTSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLESS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLESS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCMPNLESD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPNLESD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
	
def VCMPORDSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPORDSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
	
def VCMPORDSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointCompareInstruction('VCMPORDSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
	
def VPADDB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPADDW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPADDD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPADDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPSUBB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPSUBW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPSUBD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
		
def VPSUBQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPADDSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPADDSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPADDUSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDUSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPADDUSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPADDUSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSUBSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSUBSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSUBUSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBUSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSUBUSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSUBUSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMAXUB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMAXUB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMAXUW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMAXUW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMAXUD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMAXUD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMINUB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMINUB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMINUW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMINUW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMINUD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMINUD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMAXSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMAXSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMAXSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMAXSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMAXSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMAXSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMINSB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMINSB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMINSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMINSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMINSD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMINSD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPAVGB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPAVGB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPAVGW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPAVGW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSADBW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSADBW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPAND(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPAND', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPANDN(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPANDN', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPOR(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPOR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPXOR(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPXOR', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPEQB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPEQB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPEQW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPEQW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPEQD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPEQD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPEQQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPEQQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPGTB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPGTB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPGTW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPGTW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPGTD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPGTD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPCMPGTQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPCMPGTQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULUDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULUDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULLW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULLW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULHW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULHW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULHUW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULHUW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMADDWD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMADDWD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKLBW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKLBW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKLWD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKLWD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKLDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKLDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKLQDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKLQDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKHBW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKHBW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKHWD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKHWD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKHDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKHDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPUNPCKHQDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPUNPCKHQDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPACKSSWB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPACKSSWB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPACKSSDW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPACKSSDW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPACKUSWB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPACKUSWB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPACKUSDW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPACKUSDW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSIGNB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSIGNB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSIGNW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSIGNW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSIGND(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSIGND', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPHADDW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPHADDD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPHADDSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHSUBW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPHSUBW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHSUBD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPHSUBD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHSUBSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPHSUBSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHUFB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPSHUFB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULHRSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULHRSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMADDUBSW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMADDUBSW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULLD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULLD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPMULDQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxIntegerInstruction('VPMULDQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDWQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDWQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDUBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDUBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDUBD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDUBD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDUBQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDUBQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDUWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDUWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDUWQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDUWQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHADDUDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHADDUDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHSUBBW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHSUBBW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHSUBDWD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHSUBWD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPHSUBDQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = XopHorizontalAddInstruction('VPHSUBDQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSLLW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSLLW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSLLD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSLLD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSLLQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSLLQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRLW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRLW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRLD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRLD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRLQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRLQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRAW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRAW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRAD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRAD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHLB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHLB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHLW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHLW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHLD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHLD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHLQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHLQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHAB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHAB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHAW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHAW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHAD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHAD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSHAQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPSHAQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPROTB(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPROTB', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPROTW(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPROTW', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPROTD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPROTD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPROTQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = XopShiftRotateInstruction('VPROTQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSLLVD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSLLVD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSLLVQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSLLVQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRLVD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRLVD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRLVQ(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRLVQ', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPSRAVD(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxShiftInstruction('VPSRAVD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFMADDSS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFMADDSD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBSS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFMSUBSS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBSD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFMSUBSD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADDSS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFNMADDSS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADDSD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFNMADDSD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUBSS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFNMSUBSS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUBSD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4ScalarInstruction('VFNMSUBSD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDPS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMADDPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDPD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMADDPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBPS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMSUBPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBPD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMSUBPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADDPS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFNMADDPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADDPD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFNMADDPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUBPS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFNMSUBPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUBPD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFNMSUBPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUBPS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMADDSUBPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUBPD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMADDSUBPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADDPS(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMSUBADDPS', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADDPD(destination, source_x, source_y, source_z):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = Fma4VectorInstruction('VFMSUBADDPD', Operand(destination), Operand(source_x), Operand(source_y), Operand(source_z), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD132SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD132SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD132SS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD132SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD132SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD132SD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD213SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD213SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD213SS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD213SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD213SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD213SD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD231SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMADD231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD231SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMADD231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB132SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB132SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB132SS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB132SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB132SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB132SD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB213SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB213SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB213SS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB213SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB213SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB213SD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB231SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMSUB231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB231SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMSUB231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD132SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD132SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD132SS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD132SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD132SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD132SD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD213SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD213SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD213SS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD213SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD213SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD213SD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD231SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMADD231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD231SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMADD231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB132SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB132SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB132SS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB132SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB132SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB132SD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB213SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB213SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB213SS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB213SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB213SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB213SD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB231SS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMSUB231SS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB231SD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMSUB231SD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD132PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD132PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD132PS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD132PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD132PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD132PD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD213PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD213PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD213PS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD213PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD213PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADD213PD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD231PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMADD231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADD231PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADD231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMADD231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB132PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB132PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB132PS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB132PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB132PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB132PD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB213PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB213PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB213PS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB213PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB213PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUB213PD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB231PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMSUB231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUB231PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUB231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMSUB231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD132PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD132PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD132PS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD132PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD132PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD132PD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD213PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD213PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD213PS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD213PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD213PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMADD213PD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD231PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMADD231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMADD231PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMADD231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMADD231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB132PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB132PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB132PS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB132PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB132PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB132PD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB213PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB213PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB213PS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB213PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB213PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFNMSUB213PD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB231PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMSUB231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFNMSUB231PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFNMSUB231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFNMSUB231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUB132PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADDSUB132PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADDSUB132PS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUB132PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADDSUB132PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADDSUB132PD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUB213PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADDSUB213PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADDSUB213PS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUB213PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADDSUB213PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMADDSUB213PD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUB231PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADDSUB231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMADDSUB231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMADDSUB231PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMADDSUB231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMADDSUB231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADD132PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUBADD132PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUBADD132PS', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADD132PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUBADD132PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUBADD132PD', Operand(destination), Operand(source_z), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADD213PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUBADD213PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUBADD213PS', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADD213PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUBADD213PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_x:
		instruction = Fma3Instruction('VFMSUBADD213PD', Operand(destination), Operand(source_y), Operand(source_z), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_x')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADD231PS(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUBADD231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMSUBADD231PS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VFMSUBADD231PD(destination, source_x, source_y, source_z = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_z is None:
		instruction = Fma3Instruction('VFMSUBADD231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	elif destination == source_z:
		instruction = Fma3Instruction('VFMSUBADD231PD', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	else:
		raise ValueError('This FMA form requires destination == source_z')
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVSLDUP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseAvxDuplicateInstruction('MOVSLDUP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVSHDUP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseAvxDuplicateInstruction('MOVSHDUP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def MOVDDUP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseAvxDuplicateInstruction('MOVDDUP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVSLDUP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseAvxDuplicateInstruction('VMOVSLDUP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVSHDUP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseAvxDuplicateInstruction('VMOVSHDUP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VMOVDDUP(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseAvxDuplicateInstruction('VMOVDDUP', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBROADCASTSS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VBROADCASTSS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBROADCASTSD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VBROADCASTSD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBROADCASTB(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VPBROADCASTB', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBROADCASTW(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VPBROADCASTW', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBROADCASTD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VPBROADCASTD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPBROADCASTQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VPBROADCASTQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBROADCASTF128(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VBROADCASTF128', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VBROADCASTI128(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxBroadcastInstruction('VBROADCASTI128', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCVTPD2DQ(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxConvertNarrowInstruction('VCVTPD2DQ', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCVTPD2PS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxConvertNarrowInstruction('VCVTPD2PS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VCVTPS2PD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxFloatingPointVectorUnaryInstruction('VCVTPS2PD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def CVTDQ2PD(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = SseConvertInstruction('CVTDQ2PD', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VRCPSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarReciprocalInstruction('VRCPSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VRSQRTSS(destination, source_x, source_y = None):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	if source_y is None:
		destination, source_x, source_y = destination, destination, source_x
	instruction = AvxFloatingPointScalarReciprocalInstruction('VRSQRTSS', Operand(destination), Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VRCPPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxFloatingPointVectorReciprocalInstruction('VRCPPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VRSQRTPS(destination, source):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxFloatingPointVectorReciprocalInstruction('VRSQRTPS', Operand(destination), Operand(source), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VTESTPS(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxTestInstruction('VTESTPS', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VTESTPD(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxTestInstruction('VTESTPD', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction

def VPTEST(source_x, source_y):
	origin = inspect.stack() if Function.get_current().collect_origin else None
	instruction = AvxTestInstruction('VPTEST', Operand(source_x), Operand(source_y), origin = origin)
	if current_stream is not None:
		current_stream.add_instruction(instruction)
	return instruction
