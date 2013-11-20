#coding:utf-8

"""
Компонент построения структуры блога из каталога
По сути это тот же listviewdetail только для каталога
"""


def get_blogs(root, config, path="", bread_path=[]):
    pass

def build(structure, config, env={}, extra={}):
    """
    Метод запуска
    """
    get_blogs(structure, config, config.get("root", "/"))

