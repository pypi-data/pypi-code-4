def print_list(lista,level):
	for x in lista:
		if(isinstance(x,list)):
			print_list(x,level+1)
		else:
			for s in rang(level)
				print("\t",end='')
			print(x)
