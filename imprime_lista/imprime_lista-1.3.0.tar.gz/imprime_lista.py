#impressao de listas
def print_lol(a_lista, indent=false, level=0):
	for itens in a_lista:
		if isinstance(itens, list):
			print_lol(itens,indent=true,level+1) #chama novamente a funcao print_lol
		else:
			if indent:
				for num in range(level):
					print("\t", end='')
			print(itens)
