import os
import re
import sys
import time



# TODO: moze powiadamiac w jakis sposob o bledach zwiazanych z dostepem do plikow
# TODO: https://github.com/seb-m/pyinotify
# TODO: update_files - optymalizacja



class LogWatcher:

	def __init__(self, files_dict=None):
		self.__file_pattern = {}
		self.__file_path = {}
		self.__file_active = []
		if files_dict:
			for k, v in files_dict.items(): self.watch(k, v)



	@staticmethod
	def get_file_id(file_path):
		st = os.stat(file_path)
		return "%xg%x" % (st.st_dev, st.st_ino) if os.name == 'posix' else "%f" % st.st_ctime



	def watch(self, file_pattern, value=None):
		assert isinstance(file_pattern, str), Exception('`file_pattern` must by <str> !')

		if file_pattern in self.__file_pattern:
			raise Exception('I`m already watching `%s` !' % file_pattern)

		if not file_pattern:
			raise Exception('Path can`t be ampty !')

		if file_pattern[0] != '/':
			raise Exception('Path `%s` to file must by absolute !' % file_pattern)

		if '*' in file_pattern and '*' in os.path.dirname(file_pattern):
			raise Exception('`*`is allowed only in file name, not in dir path `%s` !' % file_pattern)

		self.__file_pattern[file_pattern] = value



	def unwatch(self, file_pattern):
		del self.__file_pattern[file_pattern]



	def update_files(self):

		def _match(pattern, s):
			return re.match(pattern, s) is not None


		for file_pattern in self.__file_pattern.keys():
			if '*' in file_pattern:
				dir_path, file_pattern_name = file_pattern.rsplit('/', 1)
				file_pattern_name = '^%s$' % file_pattern_name.replace('-', '\-').replace('.', '\.').replace('*', '.*')
				try:
					dl = os.listdir(dir_path)

				except (OSError, IOError) as e:
					dl = []

				for file_path in set(os.path.join(dir_path, x) for x in dl if _match(file_pattern_name, x)) - set(self.__file_pattern.keys()):
					self._update_one_file(file_pattern, file_path)

			else:
				self._update_one_file(file_pattern, file_pattern)

		self.__file_active = []
		for file_path, (file_pattern, fid, fd) in self.__file_path.items():
			if fd:
				self.__file_active.append((
					file_pattern,
					self.__file_pattern[file_pattern],
					file_path,
					fd,
				))



	def _update_one_file(self, file_pattern, file_path):
		try:
			fid = self.get_file_id(file_path)

		except (OSError, IOError) as e:
			fid = None

		if file_path in self.__file_path:
			# obserwujemy juz ten plik
			if self.__file_path[file_path][1] != fid:
				# same name but different file (rotation); reload it.
				self._open_file(file_pattern, file_path, fid)

		else:
			# nie obserwujemy jeszcze tego pliku, wiec zaczynamy to robic
			self._open_file(file_pattern, file_path, fid)



	def _open_file(self, file_pattern, file_path, fid):
		if fid:
			fd = open(file_path, 'rb')
			fd.seek(os.path.getsize(file_path))  # EOF

		else:
			fd = None

		self.__file_path[file_path] = (
			file_pattern,
			fid,
			fd,
		)



	def readline(self):
		while 1:
			self.update_files()
			if self.__file_active:
				for x in range(10):
					for file_pattern_key, file_pattern_value, file_path, fd in self.__file_active:
						try:
							for line in fd.readlines():
								yield file_pattern_key, file_pattern_value, file_path, line[:-1]

						except (OSError, IOError) as e:
							pass

					time.sleep(0.1)

			else:
				time.sleep(2)

