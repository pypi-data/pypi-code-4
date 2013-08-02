# coding=utf-8
def make_class_names(d):
    if isinstance(d, dict):
        class_names = d.pop('class', '')
    else:
        class_names = d

    if type(class_names) in (tuple, list):
        class_names = ' '.join(class_names)
    return class_names.strip()


def combine_class_names(one, two):
    name = "%s %s" % (one, two)
    return name.strip()


def extra_widget_args(renderer):
    form = renderer.form
    datas = getattr(renderer, 'widget_attrs', None)
    if type(datas) is not dict:
        return
    for name, data in datas.items():
        field = form.fields[name]
        widget = field.widget

        class_names = make_class_names(data)
        previous_classes = widget.attrs.pop('class', '')
        updated_class_names = combine_class_names(class_names, previous_classes)

        if updated_class_names != '':
            data['class'] = updated_class_names

        widget.attrs.update(data)


def extra_widget_class_names(renderer):
    form = renderer.form
    datas = getattr(renderer, 'class_names', None)
    if type(datas) is not dict:
        return

    for name, data in datas.items():
        field = form.fields[name]
        widget = field.widget

        class_names = make_class_names(data)
        previous_classes = widget.attrs.pop('class', '')
        updated_class_names = combine_class_names(class_names, previous_classes)

        if updated_class_names != '':
            widget.attrs['class'] = updated_class_names