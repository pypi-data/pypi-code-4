__author__ = 'Santi'
"""Esto es un comentario para mi modulo"""


def print_lol(lista,nivel):
    """Lo que hace este pequeño modulillo es imprimir el contenido de una lista aunque tenga listas
    :param lista:
    :param nivel:
    y además añado niveles de identación"""
    for elemento in lista:
        if isinstance(elemento,list):
            print_lol(elemento, nivel + 1)
        else:
            for tab_stop in range(nivel):
                print("\t", end ='')
            print(elemento)

