#coding:utf-8

"""
Компонент вставки данных
"""

import markdown2


def get_markdown(root, config, path=""):
    for key in root:
        item = root[key]
        if "skip" in item:
            continue

        for field in item.get("markdown", []):
            if field in item:
                text = unicode(item[field], "utf-8", errors='ignore')
                item[field] = markdown2.markdown(text)

        get_markdown(item.get("subitems", []), config, path)


def build(structure, config, env={}, extra={}):
    """
    Метод запуска
    """
    get_markdown(structure, config, config.get("path", "./"))