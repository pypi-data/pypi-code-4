import logging
import shutil

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

import argparse
import json
from itertools import imap
import os
import os.path as path

from jinja2 import Environment, FileSystemLoader

import quicksite.template_factory as tf
import quicksite.helper

# Import all the templates to be registered  - This is kind of hacky, but meh.
import quicksite.multi_template

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config",
                        help="Configuration json file")

    return parser.parse_args()

def _get_data(config_file):
    return json.load(config_file)

def _expand_here(str, here):
    retval = str.format(here=here) if "{here}" in str else str
    return retval.replace("\\", path.sep).replace("/", path.sep)


def _create_template_object(template_entry):
    return tf.template(*template_entry)


def _generate_templates(data, output_dir, template_dir):
    templates = imap(_create_template_object, data['templates'].items())
    environment = Environment(loader=FileSystemLoader(template_dir))
    for template in templates:
        template(environment, output_dir, data['data'])


def _copy_static_files(here, output_dir, static_dir):
    for (basedir, directories, files) in os.walk(static_dir):
        for file in files:
            input_file = path.abspath(path.join(basedir, file))
            output_file = input_file.replace(static_dir, output_dir)
            log.info("Copying {0}->{1}".format(input_file.replace(here, "")[1:], output_file.replace(here, "")[1:]))
            quicksite.helper.ensure_directory(output_file)
            shutil.copy2(input_file, output_file)


def do(args):

    data = _get_data(open(args.config, "r"))
    here = path.abspath(path.dirname(args.config))
    static_dir = _expand_here(data['static_dir'], here)
    template_dir = _expand_here(data['template_dir'], here)
    output_dir = _expand_here(data['output_dir'], here)

    _generate_templates(data, output_dir, template_dir)
    _copy_static_files(here, output_dir, static_dir)


def main():
    do(get_args())

if __name__ == "__main__":
    main()