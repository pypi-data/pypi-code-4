# Módulo criado para fornecer uma função chamada print_movie()
# que imprime listas que podem ou não incluir listas aninhadas.

def print_movie(lista, indent = False, nivel = 0):
    # Esta função requer um argumento posicional chamado 'lista', que é
    # qualquer lista Python (de possiveis listas aninhadas). Cada item de dados
    # na lista fornecida é (recursivamente) impresso na tela em sua própria
    # linha.
    for each_item in lista:
        if isinstance(each_item, list):
            print_movie(each_item, indent, nivel+1)
        else:
            if indent:
                for tab_stop in range(nivel):
                    print('\t', end='')
            print(each_item)
            

            
