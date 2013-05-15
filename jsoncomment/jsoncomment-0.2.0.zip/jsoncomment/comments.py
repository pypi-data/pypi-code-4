
################################################################################

from .wrapper import GenericWrapper

################################################################################

# Comments
COMMENT_PREFIX = ("#",";")
MULTILINE_START = "/*"
MULTILINE_END = "*/"

# Data strings
LONG_STRING = '"""'

################################################################################

class JsonComment(GenericWrapper):

	def loads(self, custom_json_string, *args, **kwargs):
		lines = custom_json_string.splitlines()
		standard_json = json_preprocess(lines)
		return self.object_to_wrap.loads(standard_json, *args, **kwargs)

	def load(self, custom_json_file, *args, **kwargs):
		custom_json_string = custom_json_file.read()
		return self.loads(custom_json_string, *args, **kwargs)

################################################################################

def json_preprocess(lines):

	standard_json = ""
	is_multiline = False
	keep_trail_space = 0

	for line in lines:

		keep_trail_space = 0
		if line.endswith(" "):
			keep_trail_space = 1

		line = line.strip()

		if len(line) == 0:
			continue

		if line.startswith(COMMENT_PREFIX):
			continue

		elif line.startswith(MULTILINE_START):
			is_multiline = True
			# In case both start and end are on the same line
			# Example: /***** Comment *****/
			if line.endswith(MULTILINE_END):
				is_multiline = False
			continue

		elif is_multiline:
			if line.endswith(MULTILINE_END):
				is_multiline = False
			continue

		elif LONG_STRING in line:
			line = line.replace(LONG_STRING, '"')

		standard_json += line + " " * keep_trail_space

	return standard_json

################################################################################
