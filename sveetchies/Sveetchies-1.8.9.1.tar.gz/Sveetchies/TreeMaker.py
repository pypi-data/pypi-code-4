# -*- coding: utf-8 -*-
class RawTreeMaker(object):
    """
    Calcule une arborescence à partir d'une liste d'éléments en une dimension, 
    L'arborescence calculée se fait grace aux relations (par identifiants) de 
    parentée entre tout les éléments. 
    
    @seq : une liste à plat d'objet ayant des relations de parentés entre eux
    
    @excludes : une liste d'id d'objet à exclure de l'arborescence calculée
    
    @dtd : un tuple contenant les noms clés des attributs qui servent à retracer 
    la parenté entre chaque objet. Respectivement l'id de l'objet, l'id de son 
    parent, son titre et l'ordre de tri. Le 'titre' ne sert qu'à la méthode de 
    rendu "render".
    
    @order_key : nom de clé du dictionnaire qui servira à ordonner les 
    résultats.
    """
    def __init__(self, seq=None, excludes=[], dtd=('id', 'parent', 'title'), order_key=None):
        self.__ids_dict = {}
        self.__parents_dict = {}
        self.tree = []
        self.excludes = excludes
        # Nom des clés qui nous intéressent
        self.dtd = dtd
        self._c_idkey = dtd[0]
        self._c_keyparent = dtd[1]
        self._c_keytitle = dtd[2]
        self.order_key = order_key
        
        # Formate le dictionnaire qui aide à lancer la récursivité
        for page in seq:
            page['__TreeRecurse'] = self.recurse_callback( page[self._c_idkey] )
            self.__parents_dict[ page[self._c_keyparent] ] = self.__parents_dict.get(page[self._c_keyparent], []) + [page]
            self.__ids_dict[ page[self._c_idkey] ] = page

    def recurse_callback(self, id, indent=1):
        """
        This is a closure. It curries the id for a inner method.
        The "partial" function doesn't exist yet in Python 2.4.
        """
        def inner(indent):
            return self.get_tree(id, indent=indent)

        return inner

    def get_tree(self, parent_id=None, indent=1):
        """
        Inner method récursive appelée par le callback pour stocker 
        l'arborescence en 3D
        
        @parent_id : l'id du parent à partir duquel on va calculer 
        l'arborescence. Si vide, on commence à partir de la racine.
        @indent : Ne pas toucher. Flag interne qui permet de savoir à quel 
        niveau du calcul en est la méthode, si = 1 on stock la liste calculée.
        """
        children = self.__parents_dict.get(parent_id, [])

        if not children: return []

        for child in children[:]:
            # Si l'id de l'objet est dans la liste des éléments à exclure
            if child[self._c_idkey] in self.excludes:
                del children[children.index(child)]
        
        seq = []
        for child in children:
            # Apelle l'inner method pour continuer sur les enfants
            child['__TreeChildren'] = child['__TreeRecurse'](indent=indent+1)
            del child['__TreeRecurse']
            seq.append( child )
        
        # Copie persistante interne de l'arborescence calculée
        if indent == 1:
            self.tree = seq[:]
        
        return seq
    
    def get_pathline(self, item_id=None):
        """
        Renvoi le chemin de fer/chemin d'accès du document vers la racine du site
        """
        self.__pathline = []
        self.reverse_pathline(item_id)
        self.__pathline.reverse()
        
        return self.__pathline

    def reverse_pathline(self, item_id=None):
        """
        Construction récursive du chemin de fer
        """
        page = self.__ids_dict.get(item_id, False)
        if not page:
            return []
        else:
            item = page.copy()
            del item['__TreeChildren']

        self.__pathline.append( item )
        # va chercher le parent
        self.reverse_pathline( item[self._c_keyparent] )

    def sort_list_by_dictkey(self, seq, order_key):
        """
        Méthode pour ordonner une liste de dictionnaire par une de leur clé
        """
        seq.sort(cmp=lambda x,y: cmp(x[order_key], y[order_key]))
        return seq

    def render(self, seq_list=None, indent=0):
        """
        Retourne une version formattée en texte brut d'une arborescence.
        
        @seq_list : liste des objets à traiter. Si vide, on commence depuis le 
        début de la liste calculée
        
        @indent : Indique le niveau d'indentation de départ pour l'affichage, 
        il est toujours incrémenté de 1 à chaque nouveau niveau d'enfants
        """
        string = ""
        if not seq_list:
            seq_list = self.tree
        
        # Trie la liste
        if self.order_key:
            seq_list = self.sort_list_by_dictkey(seq_list, self.order_key)

        for item in seq_list:
            string += "%s* %s\n" % ("  "*indent,item[self._c_keytitle])
            # Traite les enfants
            if len(item['__TreeChildren'])>0:
                string += self.render(item['__TreeChildren'], indent=indent+1)

        return string


class XmlTreeMaker(RawTreeMaker):
    """
    Arborescence XML d'une liste à une dimension. 
    (Exemple de classe de dérivation de "RawTreeMaker")
    """

    def render(self, seq_list=None, indent=0):
        """
        Retourne une version formattée en texte brut d'une arborescence.
        
        @seq_list : liste des objets à traiter. Si vide, on commence depuis le 
        début de la liste calculée
        
        @indent : Indique le niveau d'indentation de départ pour l'affichage, 
        il est toujours incrémenté de 1 à chaque nouveau niveau d'enfants
        """
        if indent == 0:
            rootDoc = "<root>\n%s</root>"
        else:
            rootDoc = "\n%s"
        elementsDoc = ""
        elementSingleTpl = '%s<entry id="%s" title="%s"/>\n'
        elementParentTpl = '%s<entry id="%s" title="%s">%s</entry>\n'
        
        if not seq_list:
            seq_list = self.tree
        
        # Trie la liste
        if self.order_key:
            seq_list = self.sort_list_by_dictkey(seq_list, self.order_key)

        for item in seq_list:
            # Traite les enfants
            if len(item['__TreeChildren'])>0:
                children = self.render(item['__TreeChildren'], indent=indent+1)
                elementsDoc += elementParentTpl % ("  "*indent, item[self._c_idkey], item[self._c_keytitle], children)
            else:
                elementsDoc += elementSingleTpl % ("  "*indent, item[self._c_idkey], item[self._c_keytitle])
        
        return rootDoc % elementsDoc

if __name__ == "__main__":
    # Démonstration
    import pprint
    # Liste à une dimension d'éléments de démo
    SEQTEST = [
        {'title': u'Section 5', 'id': 11, 'parent': None, 'uri': u'Section5'},
        {'title': u'Accueil', 'id': 1, 'parent': None, 'uri': u'Home'},
        {'title': u'Section 2.2.2', 'id': 10, 'parent': 7, 'uri': u'Section2-2-2'},
        {'title': u'Section 2.3', 'id': 8, 'parent': 3, 'uri': u'Section2-3'},
        {'title': u'Section 3', 'id': 4, 'parent': None, 'uri': u'Section3'},
        {'title': u'Section 2', 'id': 3, 'parent': None, 'uri': u'Section2'},
        {'title': u'Section 4.2', 'id': 13, 'parent': 5, 'uri': u'Section4-2'},
        {'title': u'Section 4', 'id': 5, 'parent': None, 'uri': u'Section4'},
        {'title': u'Section 1', 'id': 2, 'parent': None, 'uri': u'Section1'},
        {'title': u'Section 2.1', 'id': 6, 'parent': 3, 'uri': u'Section2-1'},
        {'title': u'Section 4.1', 'id': 12, 'parent': 5, 'uri': u'Section4-1'},
        {'title': u'Section 2.2', 'id': 7, 'parent': 3, 'uri': u'Section2-2'},
        {'title': u'Section 2.2.1', 'id': 9, 'parent': 7, 'uri': u'Section2-2-1'},
    ]
    
    # Calcul et rendu en texte brute
    i = 60
    s = "RAW"
    print "_"*i
    print " "*((i-len(s))/2) + s + " "*((i-len(s))/2)
    print "_"*i
    treeobject = RawTreeMaker(seq=SEQTEST, order_key='title')
    treeobject.get_tree()
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint( treeobject.tree )
    print treeobject.render()

    # Calcul et rendu en xml
    i = 60
    s = "XML"
    print "_"*i
    print " "*((i-len(s))/2) + s + " "*((i-len(s))/2)
    print "_"*i
    treeobject = XmlTreeMaker(seq=SEQTEST, order_key='title')
    treeobject.get_tree()
    print treeobject.render()

    # Recherche récursif du parent d'un élément
    i = 60
    s = "PATHLINE"
    print "_"*i
    print " "*((i-len(s))/2) + s + " "*((i-len(s))/2)
    print "_"*i
    #print treeobject.get_pathline(9)
    
    print "--- ID 2 ---"
    print " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(2)])

    print "--- ID 10 ---"
    print " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(10)])
    
    print "--- ID 5 ---"
    print " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(5)])
    
    print "--- ID 12 ---"
    print " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(12)])
