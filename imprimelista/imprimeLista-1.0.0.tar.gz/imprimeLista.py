
# Modulo que imprime lista normais e aninhadas

def imprime(lista):

# Função que recebe qualquer tipo de lista reconhecida pelo python e imprime, caso haja listas aninhadas
# é feito uso de recursividade para impressão.

	for imprimeOne in lista:
		if isinstance(imprimeOne,list):
			imprime(imprimeOne)
		else:
			print(imprimeOne)



