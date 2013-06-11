"""test my first code """
def pp_evething(the_list):
	"""print all itrms in list"""
	for each_item in the_list:
		if isinstance(each_item ,list):
			pp_evething(each_item )
		else:
			print(each_item )
			"""test my first code """