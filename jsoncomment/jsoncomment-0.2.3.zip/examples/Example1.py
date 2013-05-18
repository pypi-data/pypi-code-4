
################################################################################

try:
	import ujson as json
except ImportError:
	import json

from jsoncomment import JsonComment

################################################################################

if __name__ == '__main__':

	string = """
/******************
Comment 1
Comment 2
******************/
[
	# Objects
	{
		"key" : "value",
		"another key" :
		\"\"\"
		\\n
		A multiline string.\\n
		It will wrap to single line, 
		but a trailing space per line is kept.
		\"\"\",
	},
	; Other Values
	81,
	; Allow a non standard trailing comma
	true,
]
"""

	parser = JsonComment(json)
	parsed_object = parser.loads(string)

	print(parsed_object[0]["another key"], "\n")

	print(parser.dumps(parsed_object))

################################################################################
