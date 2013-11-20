#coding:utf-8

"""
Компонент построения навигационной цепочки
"""


def get_crumbs(root, config, path="", bread_path=[]):
    result = []
    for key in root:
        item = root[key]
        if "skip" in item:
            continue

        crumbs = {
            "name": item.get("name", item.get("title", key)),
            "path": path+key+".html",
        }

        item["breadcrumbs"] = bread_path + [crumbs]
        get_crumbs(item.get("subitems", []), config, path + item.get("folder", key) + "/", bread_path=bread_path+[crumbs])


def build(structure, config, env={}, extra={}):
    """
    Метод запуска
    """
    get_crumbs(structure, config, config.get("root", "/"))

