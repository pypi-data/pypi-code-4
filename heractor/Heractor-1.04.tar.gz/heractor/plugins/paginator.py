#coding:utf-8

"""
Компонент построения данных для листания
"""

import markdown




def get_paginator(root, config, path=""):
    for key in root:
        item = root[key]
        if "skip" in item:
            continue

        if "paginator" in item:

            object_list = item.get("subitems")
            count = count(object_list)


            get_paginator(item.get("subitems", []), config, path)


def build(structure, config, env={}, extra={}):
    """
    Метод запуска
    """
    get_paginator(structure, config)