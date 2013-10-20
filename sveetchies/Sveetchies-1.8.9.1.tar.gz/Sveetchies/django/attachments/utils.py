# -*- coding: utf-8 -*-
def get_attachment_items_from_list(attachment_list):
    """
    Renvoi un dictionnaire d'entrée de fichiers d'attachements à partir d'un queryset
    """
    res = {}
    for item in attachment_list:
        res[str(item.id)] = (item.file.url, item.title)
    return res
