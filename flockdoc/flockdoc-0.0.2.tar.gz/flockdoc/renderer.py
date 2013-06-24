import os
from jinja2 import Environment, ChoiceLoader, FileSystemLoader

loader = ChoiceLoader([
    # load current working directory templates first
    FileSystemLoader(os.path.join(os.getcwd(), 'templates')),

    # then load package templates
    FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')),
])

env = Environment(loader=loader)

