def print_list(lista):
	for x in lista:
		if(isinstance(x,list)):
			print_list(x)
		else:
			print(x)
