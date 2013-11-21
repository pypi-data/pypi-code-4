#coding:utf-8

"""
Компонент построения меню
"""


def get_menu(root, config, path=""):
    result = []
    for key in root:
        item = root[key]
        if "skip" in item:
            continue

        ri = {
            "slug": item.get("slug", key),
            "name": item.get("name", item.get("title", key)),
            "navigation": item.get("navigation", True),
            "path": path+key+".html",
            "subitems": get_menu(item.get("subitems", []), config, path + item.get("folder", key) + "/")
        }
        result += [ri]
    return result


def build(structure, config, env={}, extra={}):
    """
    Метод запуска
    """
    config["global"]["menu"] = get_menu(structure, config, config.get("root", "/"))

