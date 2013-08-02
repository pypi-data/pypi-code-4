class KoalityConfigGenerator(object):
	def __init__(self, language_generator, setup_generator, compile_generator, test_generator):
		self.language_generator = language_generator
		self.setup_generator = setup_generator
		self.compile_generator = compile_generator
		self.test_generator = test_generator

	def generate(self):
		return [
			{'languages': self.language_generator.generate()},
			{'setup': self.setup_generator.generate()},
			{'compile': self.compile_generator.generate()},
			{'test': self.test_generator.generate()}
		]
