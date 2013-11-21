#coding:utf-8

"""
Построение View/Detail структур страниц

ищет в структуре поле
object_list_data
 и
object_list_format = "json"

и прогружает оттуда данные
"""

import json, yaml


def get_list(root, config, path=""):
    for key in root:
        item = root[key]
        if "skip" in item:
            continue
        if "object_list_data" in item:
            if item.get("object_list_data_format", "json") == "json":
                item["object_list"] = json.load(file(item["object_list_data"] % config, "r"))
            elif item.get("object_list_data_format", "json") == "yaml":
                text = ""
                for line in file(item["object_list_data"] % config, "r"):
                    text += line + "\n"
                item["object_list"] = yaml.load(text)
            i = 0
            for obj in item["object_list"]:
                i += 1
                new_obj = item.get("object_list_item", {}).copy()
                #for k in obj:
                #    new_obj[k] = obj[k]
                new_obj.update(obj)
                new_obj["index"] = i
                new_obj["parent"] = {
                    "name": item.get("name", item.get("title", key)),
                    "path": path+key+".html"
                }

                obj["detail_path"] = path + item.get("folder", key) + "/" + "%s_%d.html" % (key, i)

                if not "subitems" in item:
                    item["subitems"] = {}

                item["subitems"]["%s_%d" % (key, i)] = new_obj

        get_list(item.get("subitems", []), config, path + item.get("folder", key) + "/")


def build(structure, config, env={}, extra={}):
    """
    Ищет в структуре компонент, и достраивает подэлементы
    """
    get_list(structure, config, config.get("root", "/"))