import os.path


class Reflector(object):
	def __init__(self, repo_root):
		self.repo_dir = repo_root

	def repo_relative(self, path):
		abs_repo_dir = os.path.abspath(self.repo_dir)
		return path.replace(abs_repo_dir, '').strip('/')

	def reflect(self):
		raise NotImplementedError("Subclasses should override this!")
