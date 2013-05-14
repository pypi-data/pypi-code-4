
################################################################################

from codecs import open

import ujson

from jsoncomment import JsonComment

################################################################################

if __name__ == '__main__':
	parser = JsonComment(ujson)

	with open("Example2.json", "r", "utf-8-sig") as file_json:
		parsed_object = parser.load(file_json)

		print(parsed_object["item 1"], "\n")
		print(parsed_object["Section/Subsection"], "\n")

		print(parser.dumps(parsed_object))

################################################################################
