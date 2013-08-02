from reflector import Reflector


class DatabaseReflector(Reflector):
	def reflect(self):
		return ['mysql', 'postgres']
