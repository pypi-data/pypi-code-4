
# Modulo "imprimeLista" que dispõe da função imprime que deverá imprimir Listas.

def imprime(lista, level=0):

# Função "imprime" que recebe qualquer tipo de lista reconhecida pelo python, e a quantidade de tabulação que deseja imprimir no argumento do parâmetro e imprime, caso haja listas aninhadas
# é feito uso de recursividade para impressão.
# Listas aninhadas são tabuladas na recursividade em "level"+1 para que fique sempre um caractere TAB a frente da lista pai.

	for imprimeOne in lista:
		if isinstance(imprimeOne,list):
			imprime(imprimeOne,level+1)
		else:
                        for tabulacao in range(level):
                                print("\t",end = '')
                                
                        print(imprimeOne)
