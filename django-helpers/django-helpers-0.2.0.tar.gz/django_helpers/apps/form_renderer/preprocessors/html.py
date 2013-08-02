from types import StringTypes, FunctionType
from django.utils.safestring import mark_safe


def html_preprocessor(renderer):
    form = renderer.form
    before = getattr(renderer, 'html_before', None)
    after = getattr(renderer, 'html_after', None)

    if type(before) is dict:
        return

    for datas, attr in ((before, 'html_before'), (after, 'html_after')):
        if type(datas) is not dict:
            continue

        for name, data in datas.items():
            field = form.fields[name]
            html = None
            typ = type(data)

            if typ in StringTypes:
                html = data

            elif typ in (tuple, list):
                html = "\n".join(data)

            elif typ is FunctionType:
                html = data()

            setattr(field, attr, mark_safe(html))