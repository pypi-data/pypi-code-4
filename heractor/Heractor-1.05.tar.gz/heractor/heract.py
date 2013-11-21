#!/usr/bin/env python
#coding:utf-8

import getopt
import sys
import os
from json import load

try:
    from jinja2 import Environment, FileSystemLoader
except:
    print "Install Jinja2 templates (pip install jinja2)"
    sys.exit()

verbose = False


def plugins(config, structure):
    if "plugins" in config:
        if not "global" in config:
            config["global"] = {}

    def get_method(string_name):
        _tmp = string_name.split(".")
        modl = __import__(".".join(_tmp[:-1]), globals(), locals(), [], -1)
        return getattr(getattr(modl, _tmp[-2]), _tmp[-1])

    for path_method in config.get("plugins", []):
        plugin = get_method(path_method)
        v("%s (%s) loaded" % (path_method, plugin))
        plugin(structure, config)


def heract(config):
    """
    Основной метод построения сайта
    """
    path = config.get("path", "./")
    v("Set path %s" % path)
    v("Load structure %s" % config.get("structure", "structure.json"))
    structure = load(file(config.get("structure", "structure.json")))
    jinja_env = Environment(loader=FileSystemLoader(config.get("templates", ""), encoding='utf-8'),
                            autoescape=True)

    plugins(config, structure) # Подключим модули
    v("Global:")
    v(config["global"])

    # Начнем построение

    def build(root, config, jinja_env, henv, url_path, file_path):
        for key in root:
            v("Build key %s" % key)
            item = root[key]
            if item.get("skip", False):
                continue

            _henv = henv.copy()
            _henv.update(item)

            page_path = os.path.join(file_path, key+".html")

            if "template" in _henv:
                f = file(page_path, "w")
                _henv["path"] = path + key + ".html"
                text = jinja_env.get_template(_henv.get("template", ""), globals=config.get("global", {})).render(_henv)
                f.write(text.encode(encoding="utf-8", errors="strict"))
                f.close()
            if "subitems" in item:
                if not os.path.exists(os.path.join(file_path, item.get("folder", key)+"/")):
                    os.mkdir(os.path.join(file_path, item.get("folder", key)+"/"))
                build(item["subitems"], config, jinja_env, _henv,
                      url_path=os.path.join(url_path, item.get("folder", key)+"/"),
                      file_path=os.path.join(file_path, item.get("folder", key)+"/"))

    build(structure, config, jinja_env, {}, url_path=config.get("root", "/"),
          file_path=config.get("out", "./"))


def get_base(base_config, base_section):
    if "base" in base_config[base_section]:
        v("Applay base section %s" % base_config[base_section]["base"])
        config = get_base(base_config, base_config[base_section]["base"])
    else:
        config = {}

    config.update(base_config[base_section])
    return config


def applay_config_vars(root, config):
    """
    Применяет данные конфига к другим элементам этого же конфига :)
    """
    for key in root:

        if isinstance(root[key], basestring):
            print "Applay keys to root %s" % key
            root[key] = root[key] % config
        elif isinstance(root[key], dict):
            applay_config_vars(root[key], config)


def preparation_config(config_file, config_section, extra=[]):
    """
    Прогружает конфигурационный фаил и пременяет на него все секции
    """
    v("Load config %s" % config_file)
    config = get_base(load(file(config_file)), config_section)
    config["path"] = config.get("path", "./")
    config["abspath"] = os.path.abspath(config["path"])
    v("abspath:%s" % config["abspath"])
    applay_config_vars(config, config)
    return config


def v(text):
    """
    Verbose
    """
    global verbose
    if verbose:
        if text.__class__ == dict or text.__class__ == list:
            print repr(text).decode("unicode-escape")
        else:
            print text


def usage():
    print('''Heractor v.1.0
 Description:
    Static site generator

 Help:
    --help          display help
    --config=       select config file (default: config.json)
    --section=      config file section (default: main)
    --verbose       verbose mode
    ''')


def main():
    global verbose
    config_file = "config.json"
    config_section = "main"

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:vs:', ["help", "config=", "verbose", "section="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit()

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--config"):
            config_file = a
        elif o in ("-s", "--section"):
            config_section = a
        else:
            usage()
            sys.exit()

    config = preparation_config(config_file, config_section)
    heract(config)

if __name__ == "__main__":
    main()