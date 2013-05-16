import sys

__input_file = None
__output_file = None

class PrintHook:
	def __init__(self, output_file):
		self.file_stdout = output_file
		self.real_stdout = sys.__stdout__

	def write(self, text):
		self.file_stdout.write(text)
		self.real_stdout.write(text)

	def __getattr__(self, name):
		return self.real_stdout.__getattr__(name)

def load_input(in_filename):
	global __input_file, __output_file

	__input_file = open(in_filename)
	out_filename = in_filename.replace('.in', '') + '.out'
	__output_file = open(out_filename, 'w')
	sys.stdout = PrintHook(__output_file)

def read_input(*lines):
	global __input_file

	if __input_file is None:
		if len(sys.argv) < 2:
			raise ValueError('Must specify input file with load_input() or on command line')
		load_input(sys.argv[1])

	inputs, repeats, repeating = [], 1, False
	for line in lines:
		if line == '':
			__input_file.readline()
			continue
		elif type(line) is int:
			repeats = line
			repeating = True
		else:
			formats = line.split()
			
			new_inputs = []
			next_repeats = 1
			next_repeating = False
			for repeat in range(repeats):
				if len(formats) == 1 and '[' not in formats[0]:
					data = [__input_file.readline().strip()]
				else:
					data = __input_file.readline().split()

				this_set = []
				for i, format in enumerate(formats):
					if format == 'i->':
						next_repeating = True
						next_repeats = int(data[i])
						this_set += [next_repeats]
						continue

					if 's' in format: a_converter = str
					if 'i' in format: a_converter = int
					if 'f' in format: a_converter = float
					if '{' in format:
						converter = lambda x: map(a_converter, list(x))
					else:
						converter = a_converter

					if '[' in format:
						data_list = map(converter, data[i:])
						if '[<]' in format: data_list.sort()
						if '[>]' in format: data_list.sort(reverse = True)
						this_set += [data_list]
					else:
						this_set += [converter(data[i])]

				if repeating and len(formats) > 1:
					this_set = [this_set]
				
				new_inputs += this_set

			if repeating:
				new_inputs = [new_inputs]
			inputs += new_inputs

			repeats = next_repeats
			repeating = next_repeating

	return inputs if len(inputs) > 1 else inputs[0]