# -*- coding: utf-8 -*-
import os
import urllib
from jinja2 import Environment, BaseLoader, TemplateNotFound


class Template():
    """Class to handle templates."""

    def __init__(self, dir_templates):
        """Initialize template environment."""

        self.vars = {}
        self.doc_vars = {}
        self.dir_templates = dir_templates
        self.env = Environment(loader=TemplateLoader(self.dir_templates))
        # add urlencode filter to template
        self.env.filters['urlencode'] = lambda x: urllib.quote_plus(x)

    def get_env(self):
        """Return template environment."""

        return self.env

    def add_var(self, name, value):
        """Add to template variables."""

        self.vars[name] = value

    def add_doc_var(self, name, value):
        """Add to template variables."""

        self.doc_vars[name] = value

    def empty_doc_vars(self):
        """Empty doc_vars dictionary."""

        self.doc_vars = {}

    def get_var(self, name):
        """Return value of template variables with given name."""

        return self.vars[name]

    def get_vars(self):
        """Return non doc-specific template variables."""

        return self.vars

    def get_all_vars(self):
        """Return alltemplate variables combines."""

        all_vars = self.vars.copy()
        all_vars.update(self.doc_vars)
        return all_vars


class TemplateLoader(BaseLoader):

    """Class to handle template Loading."""

    def __init__(self, path):
        """Set template path."""

        self.path = path

    def get_source(self, environment, template):
        """Set template source."""

        path = os.path.join(self.path, template)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)
