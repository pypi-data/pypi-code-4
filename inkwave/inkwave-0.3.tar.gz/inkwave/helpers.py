from inkwave.core import (
    helper,
    env,
)


@helper
def url(name, *args, **kwargs):
    return env.build_url(name, *args, **kwargs)


@helper
def link(text, name, *args, title=None, **kwargs):
    if title:
        title = ' title="{}"'.format(title)
    return '<a href="{}"{}>{}</a>'.format(url(name, *args, **kwargs),
                                          title,
                                          text)
