import os
import sys

from jinja2 import Environment, ChoiceLoader, FileSystemLoader
from . import template_path

loader = ChoiceLoader([
    # load current working directory templates first
    FileSystemLoader(os.path.join(os.getcwd(), 'templates')),

    # then load package templates
    # when packaged:
    FileSystemLoader(os.path.join(sys.prefix, template_path)),

    # in development:
    FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')),
])

env = Environment(loader=loader)

