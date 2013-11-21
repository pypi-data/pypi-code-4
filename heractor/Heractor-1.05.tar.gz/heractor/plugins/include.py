#coding:utf-8

"""
Компонент вставки данных
"""

import json, yaml

def get_datas(root, config, path=""):
    result = []
    for key in root:
        item = root[key]
        if "skip" in item:
            continue

        if "include" in item:
            data_format = item.get("include_format", "json")
            file_name = item["include"] % config

            if "#" in file_name:
                _tmp = file_name.split("#")
                file_name = _tmp[0].strip()
                section = _tmp[1]


            if data_format in ["json", "yaml"]:
                if data_format == "json":
                    data = json.load(file(file_name, "r"))
                elif data_format == "yaml":
                    text = ""
                    for line in file(file_name, "r"):
                        text += line + "\n"
                    data = yaml.load(text)

                if section:
                    data = data[section]

                #for key in data:
                #    item[key] = data[key]
                item.update(data)

            elif data_format in ["text"]:
                _tmp = file_name.split("#")
                text = ""
                file_name = _tmp[0].strip()
                for line in file(file_name, "r"):
                    text += line
                item["include"] = text


        get_datas(item.get("subitems", []), config, path)


def build(structure, config, env={}, extra={}):
    """
    Метод запуска
    """
    get_datas(structure, config, config.get("path", "./"))