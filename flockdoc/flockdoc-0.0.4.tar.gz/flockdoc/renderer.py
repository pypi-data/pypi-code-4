import os
import sys

from jinja2 import Environment, ChoiceLoader, FileSystemLoader
from . import template_path

loader = ChoiceLoader([
    # load current working directory templates first
    FileSystemLoader(os.path.join(os.getcwd(), 'templates')),

    # then load package templates
    FileSystemLoader(template_path),
])

env = Environment(loader=loader)
