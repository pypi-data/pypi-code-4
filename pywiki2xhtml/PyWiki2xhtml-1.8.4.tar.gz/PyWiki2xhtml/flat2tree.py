# -*- coding: utf-8 -*-
"""
Mise en arborescence de liste "plate"

TODO: Un peu vieux, il faudrait virer ce module et utiliser ``Sveetchies.TreeMaker`` à la 
place.
"""
class flatList_to_Tree:
    """
    Récupère une liste d'éléments en une dimension ou chaque objet comporte
    un indice de niveau par importance décroissante et en ressort une liste
    arborescente. Il n'y a pas de logique corrective, si il y a des décalages
    entres les niveaux d'importances donnés, leur enfants ne seront simplement
    pas traités, mais par contre il n'y aura rien de cassé.
    Voir la fonction main() plus bas pour un exemple du format d'entrée
    """
    def __init__(self, source_dict):
        self.dict_1D = source_dict
        self.__byLevel = {}
        self.__withParent = {}
        self.dict_tree = {}
        # Lance le travail de recherche et formattage
        self.__findAllParent()
        self.__makelistByLevel()

    def __findAllParent(self):
        """
        Lance la recherche de parenté pour chaque item
        """
        for k,v in self.dict_1D.items():
            self.__withParent[k] = v.copy()
            self.__findItemParent(k, v)

    def __findItemParent(self, id, values):
        """
        Va chercher le parent dans l'aborescence d'un item
        """
        # Récupère la liste des id dans le bon sens
        maybe_parent_list = range(id)
        maybe_parent_list.reverse()
        #
        actual_level = values['lv']
        #
        for row in maybe_parent_list:
            if row > 0 and self.__withParent[row]['lv'] > actual_level:
                self.__withParent[id]['parent'] = row
                break
            else:
                self.__withParent[id]['parent'] = 0

    def __makelistByLevel(self):
        """
        Reformate une liste à plat avec des niveaux croissants qui se suivent
        et récupère l'idparent de chaque item
        """
        by_titlesLevel = {}
        for k,v in self.dict_1D.items():
            in_level = v['lv']
            # dico par niveaux d'importances, les plus gros étant prévu pour
            # aller au plus bas de la liste
            if not by_titlesLevel.has_key(in_level):
                by_titlesLevel[in_level] = {}
            by_titlesLevel[in_level][k] = v.copy()
            # rajout du parent
            by_titlesLevel[in_level][k]['parent'] = self.__withParent[k]['parent']
            del by_titlesLevel[in_level][k]['lv']
        # D'après la liste par niveaux des titres et celle avec le parent, on
        # reformate une liste par niveaux de profondeur
        lv_keys = by_titlesLevel.keys()
        lv_keys.reverse()
        i = 1
        # d'après les clés de la liste par niveau des titres, on refait une liste
        # indicée par des niveaux débutant à 1
        for Hx in lv_keys:
            self.__byLevel[i] = by_titlesLevel[Hx].copy()
            i += 1

    def displayTreeForWiki(self):
        # niveau root
        if not self.__byLevel.has_key(1): return ''
        s = ''
        # récupère la liste des items du niveau, dans un ordre croissant
        asc_keys = self.__byLevel[1].keys()
        asc_keys.sort()
        # liste chaque item
        for ascKey in asc_keys:
            self.dict_tree[ascKey] = self.__byLevel[1][ascKey].copy()
            s += "* %s\n" % self.__byLevel[1][ascKey]['title']
            # va chercher les enfants
            s += self.__recursiveDisplayTfW(ascKey)
        return s

    def __recursiveDisplayTfW(self, idparent, level=2):
        """
        Recherche récursive d'enfants
        """
        if not self.__byLevel.has_key(level): return ''
        s = ''
        # récupère la liste des items du niveau, dans un ordre croissant
        asc_keys = self.__byLevel[level].keys()
        asc_keys.sort()
        # liste chaque item qui est parent de l'idparent donné
        for ascKey in asc_keys:
            if self.__byLevel[level][ascKey]['parent'] == idparent:
                s += "%s %s\n" % ( ('*'*level), self.__byLevel[level][ascKey]['title'] )
                # on continue la recherche récursivement dans des niveaux plus
                # profonds tant qu'il en reste
                if level+1 in self.__byLevel.keys():
                    s += self.__recursiveDisplayTfW(ascKey, level=level+1)
        return s
    
    def output_debug(self):
        # debug liste de base
        print 'Base'
        print '-'*5
        for k,v in self.dict_1D.items():
            print str(k)+": "+str(v)
        # debug liste avec parentée
        print '_'*20
        print 'WithParent'
        print '-'*5
        for k,v in self.__withParent.items():
            print str(k)+": "+str(v)
        # debug liste par niveaux de profondeur
        print '_'*20
        print 'ByRealLevel'
        print '-'*5
        for k,v in self.__byLevel.items():
            print str(k)+": "+str(v)


def main():
    """
    Fonction appelée par défaut en ligne de commande
    """
    dict = {
        1 : {'title':'Row 1', 'lv':4},
        2 : {'title':'Row 1.1', 'lv':3},
        3 : {'title':'Row 1.1.1', 'lv':2},
        4 : {'title':'Row 1.1.2', 'lv':2},
        5 : {'title':'Row 2', 'lv':4},
        6 : {'title':'Row 2.1', 'lv':3},
        7 : {'title':'Row 2.2', 'lv':3},
        8 : {'title':'Row 2.3', 'lv':3},
        9 : {'title':'Row 2.3.1', 'lv':2},
        10 : {'title':'Row 3', 'lv':4},
        11 : {'title':'Row 4', 'lv':4},
    }
    # traite la chaine nettoyée par l'interface rajoutée pour htmldata
    print '#'*60
    print "VERSION PROPRE"
    print '#'*60
    obj = flatList_to_Tree(dict)
    print obj.displayTreeForWiki()

    gruik_dict = {
        1 : {'title':'Row 1', 'lv':5},
        2 : {'title':'Row 1.1', 'lv':3},
        3 : {'title':'Row 1.1.1', 'lv':2},
        4 : {'title':'Row 1.1.2', 'lv':2},
        5 : {'title':'Row 2', 'lv':4},
        6 : {'title':'Row 2.1', 'lv':3},
        7 : {'title':'Row 2.2', 'lv':3},
        8 : {'title':'Row 2.3', 'lv':3},
        9 : {'title':'Row 2.3.1', 'lv':2},
        10 : {'title':'Row 3', 'lv':4},
        11 : {'title':'Row 4', 'lv':4},
    }
    # traite la chaine nettoyée par l'interface rajoutée pour htmldata
    print '#'*60
    print "VERSION AVEC UNE LISTE FOIREUSE"
    print '#'*60
    obj = flatList_to_Tree(gruik_dict)
    print obj.displayTreeForWiki()

if __name__ == "__main__":
    main()
