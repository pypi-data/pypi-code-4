# coding=utf-8
import importlib


def class_for_path(class_path):
    module_name, class_name = class_path.rsplit(".", 1)
    m = importlib.import_module(module_name)
    c = getattr(m, class_name)
    return c
