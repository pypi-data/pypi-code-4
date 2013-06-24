"functions for handling markdown pages"
from . import Page

class StaticPage(Page):
    'pass a page through as-is'
    def render(self, template=None):
        'render code content, returning filename and content'
        return self.filename, self.content
