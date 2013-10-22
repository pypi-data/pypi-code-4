# -*- coding: utf-8 -*-
from django.template import Library
from django.conf import settings

register = Library()

@register.filter
def dictget(dictionnary, index):
    """
    Renvoi la valeure d'une entrée d'un dictionnaire
    
    Méthode silencieuse qui ne lève pas d'exception si la clé n'existe pas dans le 
    dictionnaire fournit.
    
    NOTE: Cette méthode date d'une époque ou les templates de Django ne permettait pas 
          d'accéder simplement aux éléments d'un dictionnaire. Elle ne devrait plus avoir 
          d'utilité réelle maintenant.
    
    :type dictionnary: dict
    :param dictionnary: Un dictionnaire python contenant la valeur à récupérer
    
    :type index: any
    :param index: Clé de la valeur à récupérer
    
    :rtype: any
    :return: Valeur à récupérer ou False si sa clé n'a pas été retrouvée
    """
    return dictionnary.get(index, False)

@register.filter
def tupleget(tup, index):
    """
    Renvoi l'entrée demandée dans le tuple
    
    NOTE: De même que ``dictget`` cette méthode a peu d'utilité réelle dans le cadre de 
          Django >= 1.x
    
    :type tup: tuple or list
    :param tup: Liste où retrouver l'élément recherché.
    
    :type index: int
    :param index: Indice de position de l'élément dans la liste.
    
    :rtype: any
    :return: Valeur correspondant à l'élément ciblé par l'indice de position spécifié.
    """
    return tup[index]

@register.filter
def truncatestring(value, limit=125):
    """
    Coupe une chaine après un certains nombre de caractères
    
    La coupure se fait si la chaîne originale fournie dépasse la limite, dans ce cas la 
    coupure se fait alors sur ``limit-2`` caractères, les deux derniers caractères étant 
    réservés au suffixe ``..`` qui indique que la ligne a été coupée.
    
    :type value: string
    :param value: Valeur à couper si elle est plus longue que la limite.
    
    :type limit: int
    :param limit: (optional) Limite du nombre de caractères alloués pour la valeur. Par 
                  défaut, la limite est placée à 125caractères.
    
    :rtype: string
    :return: Valeur coupée si elle dépasse la limite
    """
    # Si la chaine est plus longue on coupe juste avant le dernier espace
    # trouvé avant la limite
    if len(value)>limit:
        s = value[0:limit+2]
        endindex = s.rfind(" ")-2
        if endindex < 0:
            endindex = limit
        return value[0:endindex+2]+".."
    return value

@register.filter
def cut_words_length(words, limit=26):
    """
    Coupe tout les mots qui font plus de X caractères.
    
    Le compte des mots se fait par une simple séparation sur les caractères "blancs" 
    (espaces, tabulation, saut de lignes,..).
    
    :type words: string
    :param words: Chaîne de caractères
    
    :type limit: int
    :param limit: (optional) Limite du nombre de mots avant la coupure. Par défaut 
                  la limite est placée à 26mots.
    
    :rtype: string
    :return: Chaîne de caractères au bout du nombre maximum de mots autorisés.
    """
    seq = []
    for word in words.split():
        if len(word)>limit:
            word = word[:limit]
        seq.append(word)
    
    return ' '.join(seq)
