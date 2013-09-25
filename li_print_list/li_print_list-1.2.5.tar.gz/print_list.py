def print_list(lista,level=0):
	for x in lista:
		if(isinstance(x,list)):
			print_list(x,level+1)
		else:
			for s in range(level):
				print("\t",end='')
			print(x)
