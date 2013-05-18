#TODO: add task to deploy app to dev/production server
#TODO: add git support
#TODO: add comments and update function docs
#TODO: push old manifest map variable into manifest.py

import shutil
import os
import hashlib
import imp
from collections import deque

from jinja2 import Environment, DictLoader

from utils import *
from v12.cachebuster import ManifestDataUtil
from v12.routing import RoutesDataUtil
from v12 import env


def compile_template(filepath):
    if os.path.splitext(filepath)[1][1:] == "jade":
        template_text = shell("pyjade -c jinja " + filepath, capture=True)
    else:
        with open(filepath) as template_file:
            template_text = template_file.read()
    env = Environment(loader=DictLoader({os.path.basename(filepath): template_text}))
    output_path = os.path.splitext(filepath)[0] + ".py"
    ext = os.path.splitext(filepath)[1][1:]
    env.compile_templates(output_path, [ext], None)  # array is extension array, leave blank or retrieve ext


def render_template(filepath):
    with open(filepath) as template_file:
        template_text = template_file.read()
    env = Environment(loader=DictLoader({os.path.basename(filepath): template_text}))
    env.globals["manifest"] = ManifestDataUtil
    output_path = os.path.splitext(filepath)[0]

    with open(output_path, "w") as output_file:
        output_file.write(env.get_template(os.path.basename(filepath)).render())


@datafile_modifier(RoutesDataUtil)
def register_handler(filepath, project_path, app_config):
    for path in os.environ['PATH'].split(os.pathsep):
        appserver_path = os.path.join(path, 'dev_appserver.py')
        if os.path.exists(appserver_path):
            break

    dev_appserver = imp.load_source('dev_appserver', appserver_path)
    dev_appserver.fix_sys_path()

    for handler_config in app_config["handlers"]:
        if "script" in handler_config:
            script_path = os.path.join(project_path, handler_config["script"].replace(".app", ".py"))
            print script_path
            imp.load_source(os.path.basename(script_path)[:-3], script_path)

    include_path = os.path.dirname(filepath)
    package_list = deque()
    while "__init__.py" in os.listdir(include_path):
        package_list.appendleft(os.path.basename(include_path))
        include_path = os.path.dirname(include_path)

    if package_list:
        import_path = ".".join(package_list)
    else:
        return

    imp.load_source(import_path, filepath)


@datafile_modifier(ManifestDataUtil)
def fingerprint(filepath, output_dir="", key="", stylesheet="", script="", keep_source=True):
    with open(filepath) as file:
        hash = hashlib.md5(file.read()).hexdigest()

    if hash not in filepath:
        ext = os.path.basename(filepath)[os.path.basename(filepath)[1:].find(".") + 1:]
        base_filename = os.path.basename(filepath)[:-len(ext)]
        if output_dir:
            output_dir = os.path.abspath(output_dir)
        else:
            output_dir = os.path.dirname(os.path.abspath(filepath))

        fingerprinted_filepath = os.path.join(output_dir, base_filename + "-" + hash + ext)
        fingerprinted_url = fingerprinted_filepath[len(env.project_path):]

        filepath = os.path.abspath(filepath)

        if not key:
            key = filepath[len(env.project_path):]

        if keep_source:
            shutil.copy(filepath, fingerprinted_filepath)
        else:
            os.rename(filepath, fingerprinted_filepath)

        ManifestDataUtil.map(key, fingerprinted_url)

        if stylesheet:
            with open(stylesheet, "w") as stylesheet_file:
                stylesheet_file.write("." + base_filename + "{ background: url('" + fingerprinted_url +
                                      "') no-repeat; }")

        if script:
            with open(script, "w") as script_file:
                script_file.write("var manifest = manifest || {};" + os.linesep +
                                  "manifest['" + key + "'] = '" + fingerprinted_url + "';")
