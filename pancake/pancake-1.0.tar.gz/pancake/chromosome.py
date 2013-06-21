class Chromosome:

	def __init__(self, name, genome):
		self.name = name
		self.genome = genome #string 'GENOME_NAME'

	def __str__(self):
		'''will be used for pangenome output'''
		return self.name #+' (' + self.genome + ')'

	def new_name(self, new_name):
		'''rename Chromosome'''
		self.name = new_name

	def add_to_genome(self, genome):
		self.genome = genome


