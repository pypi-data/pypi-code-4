import yaml
from markdown import markdown


META_SEPARATOR = '----'
MARKDOWN_EXTENSIONS = [
    'extra',
    'codehilite',
    'toc',
]


def load_markdown(text):
    end = text.find(META_SEPARATOR)
    if end >= 0:
        meta = yaml.load(text[0:end])
        meta['content'] = markdown(
            text[end+len(META_SEPARATOR):],
            MARKDOWN_EXTENSIONS
        )
        return meta
    return {'content': markdown(text)}
