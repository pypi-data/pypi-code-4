from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class SlugConverter(RegexConverter):

    def __init__(self, url_map, *items):
        items = [r"^[a-zA-Z0-9-]+$"]
        super(SlugConverter, self).__init__(url_map, *items)
