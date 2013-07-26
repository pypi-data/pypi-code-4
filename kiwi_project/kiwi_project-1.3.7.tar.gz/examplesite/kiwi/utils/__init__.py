# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from Sveetchies.django.TreeMaker import TemplatedTree

def get_root_element(seq, item_id):
    # Calcule l'arborescence
    treeobject = TemplatedTree(seq=seq)
    treeobject.get_tree()
    # Récupère uniquement le premier élément de la liste qui est forcément la 
    # racine de l'arborescence
    root = treeobject.get_pathline(item_id)[0]
    return urlify_wikipage_object(root)

def urlify_wikipage_object(pageDict):
    pageDict['uri_slug'] = pageDict['uri']
    pageDict['uri'] = reverse('kiwi.views.wikipage.details', args=[], kwargs={'uri':pageDict['uri']})
    return pageDict

def get_attachment_items_from_list(attachment_list):
    """
    Renvoi un dictionnaire d'entrée de fichiers d'attachements à partir d'un queryset
    """
    res = {}
    for item in attachment_list:
        res[str(item.id)] = (item.file.url, item.title)
    return res
