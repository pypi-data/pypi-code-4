
################################################################################

import ujson

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
				A multiline string.\\n
				No spacing or formatting is saved, 
				the whole line is joined with all edge spaces
				trimmed.
				\"\"\"
			},
			; Other Values
			81,
			true
		]
	"""

	parser = JsonComment(ujson)
	parsed_object = parser.loads(string)

	print(parsed_object[0]["another key"], "\n")

	print(parser.dumps(parsed_object))

################################################################################
