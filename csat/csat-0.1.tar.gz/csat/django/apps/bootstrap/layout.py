from crispy_forms import layout


class ButtonLink(layout.HTML):
    def __init__(self, text, name=None, url=''):
        if name is not None:
            # TODO: Call reverse here instead?
            url = "{{% url '{}' %}}".format(name)

        html = u'<a href="{}" class="btn btn-link">{}</a>'.format(url, text)
        super(ButtonLink, self).__init__(html)


class Title(layout.HTML):
    def __init__(self, text):
        html = u'<h1 class="form-title">{}</h1>'.format(text)
        super(Title, self).__init__(html)


class IconButton(layout.HTML):
    def __init__(self, text, icon, **attrs):
        if 'css_class' in attrs:
            attrs['class'] = attrs['css_class']
            del attrs['css_class']

        attrs = ['{}="{}"'.format(k, v) for k, v in attrs.iteritems()]
        attrs = ' '.join(attrs)
        if attrs:
            attrs = ' ' + attrs

        html = u'<button{}><i class="icon-{}"></i> {}</button>'.format(
            attrs, icon, text)
        super(IconButton, self).__init__(html)
