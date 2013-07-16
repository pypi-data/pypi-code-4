# -*- coding: utf-8 -*-
from flask.ext.script import Command, Option
from pkgutil import get_data
from jinja2 import Template


class Initialize(Command):
    """Show the name and package of the application.
    """

    name = 'init'

    def run(self):
        data = get_data('alchemist', 'templates/init/setup.py')
        template = Template(data.decode('utf8'))
        text = template.render(name='application')
        print(text)
