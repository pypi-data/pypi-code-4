# coding=utf-8
from django.forms import Field, Widget


def replace_widgets(renderer):
    form = renderer.form
    datas = getattr(renderer, 'replace_widgets', None)
    if type(datas) is not dict:
        return

    if len(datas) == 0:
        return

    for name, field in form.fields.items():
        if isinstance(field, Field):
            old_widget = field.widget
            if isinstance(old_widget, Widget):
                widget_cls = type(field.widget)
                new_cls = datas.get(widget_cls)
                if new_cls is None:
                    continue
                if isinstance(new_cls, type):
                    new_cls = new_cls()
                if isinstance(new_cls, Widget):
                    new_cls.is_localized = old_widget.is_localized
                    new_cls.is_required = old_widget.is_required
                    field.widget = new_cls