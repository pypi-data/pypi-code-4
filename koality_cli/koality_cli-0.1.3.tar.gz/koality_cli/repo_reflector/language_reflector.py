import collections
import os

from reflector import Reflector

VALID_EXTENSIONS = [
	# '.c',
	'.clj',
	'.coffee',
	# '.cpp',
	# '.erl',
	# '.go',
	'.java',
	'.js',
	'.py',
	'.rb',
	'.scala'
]


class LanguageReflector(Reflector):
	def reflect(self):
		extensions = []

		for root, dirs, files in os.walk(self.repo_dir):
			if '.git' in dirs:
				dirs.remove('.git')

			if '.git' in files:
				del dirs[:]
			else:
				for name in files:
					_, ext = os.path.splitext(name)
					if (extensions.count(ext) == 0) & (ext in VALID_EXTENSIONS):
						extensions.append(ext)

		return extensions
