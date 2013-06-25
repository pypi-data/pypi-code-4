'base class for content pages'

class Page(object):
    def __init__(self, filename, content):
        self.filename, self.content = filename, content

    def render(self, template=None):
        raise NotImplementedError
