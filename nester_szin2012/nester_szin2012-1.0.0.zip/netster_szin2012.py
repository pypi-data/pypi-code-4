ms = ["the holy frail", 1975,
      "the life of brian", 91,
	  ["graham",
		["mic", "hohn", "terry", "eric", "jones"]
		]]



def print_lo(the_list):
	for line in the_list:
		if isinstance(line, list):
			print_lo(line)
		else:
			print line


