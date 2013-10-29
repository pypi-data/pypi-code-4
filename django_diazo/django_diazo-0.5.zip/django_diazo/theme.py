

class DiazoTheme(object):
    name = ''
    slug = ''
    prefix = ''


class ThemeRegistry(object):
    def __init__(self):
        self._registry = set()

    def register(self, cls):
        if issubclass(cls, DiazoTheme):
            self._registry.add(cls)

    def get_themes(self):
        for theme in self._registry:
            yield theme


registry = ThemeRegistry()
