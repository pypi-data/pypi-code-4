#coding:utf-8


def get_page_info(root, config, path):
    result = []
    for key in root:
        item = root[key]
        if "skip" in item:
            continue
        result += [{
            "slug": item.get("slug", key),
            "name": item.get("name", item.get("title", key)),
            "path": path+key+".html",
        }]
        result += get_page_info(item.get("subitems", []), config, path + item.get("folder", key) + "/")
    return result


def build(structure, config, env={}, extra={}):
    config["global"]["pages"] = {}
    for item in get_page_info(structure, config, config.get("root", "/")):
        config["global"]["pages"][item["slug"]] = item