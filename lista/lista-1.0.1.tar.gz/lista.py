#author.: gustavo xavier saquetta
#data...: 05/11/2013

#funcao para imprimir listas dentro de listas
def imprime_lista (param_lista,level):
	#procura uma lista dentro da outra
	for itens in param_lista:
		#se existe uma lista instanciada dentro de outra
		if isinstance(itens, list):
			#verdadeiro: chama a si mesmo "recursividade"
			imprime_lista(itens,level+1)
		else:
			for tabulacao in range(level):
				print("\t",end='')
			#falso: imprime todas listas até não ter mais nehuma
			print(itens)

