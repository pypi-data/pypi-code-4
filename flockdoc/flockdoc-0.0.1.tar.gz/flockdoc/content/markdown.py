"functions for handling markdown pages"
from __future__ import absolute_import

from markdown import markdown
import yaml

from . import Page
from ..renderer import env

class MarkdownPage(Page):
    'render a page as markdown'
    def __init__(self, filename, content):
        self.filename = filename
        self.meta, self.content = content.split('---', 1)
        self.meta = yaml.safe_load(self.meta)

    def render(self, template='layouts/default.html'):
        'render code content, returning filename and content'
        basename = self.filename.rsplit('.', 1)[0]
        tmpl = env.get_template(template)

        rendered = tmpl.render(
            content=env.from_string(markdown(self.content)).render(**self.meta),
            **self.meta
        )

        return basename + '.html', rendered
