# -*- coding: utf-8 -*-
def startswith_in_list(src, items):
    """
    Comparaison de type "startswith" avec une liste de 'match' possibles
    """
    for k in items:
        if src.startswith(k):
            return k
    return False

def endswith_in_list(src, items):
    """
    Comparaison de type "endswith" avec une liste de 'match' possibles
    """
    for k in items:
        if src.endswith(k):
            return k
    return False
