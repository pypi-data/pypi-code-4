# coding=utf-8
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date
from . import DataTableColumn, get_value
from django_helpers.utils.bootstrap import link_button, generate_code, link_button_set


class BootstrapButtonColumn(DataTableColumn):
    def __init__(self, text, color, link, icon='', size=None, title_class=None, title_width="20px", title='', field='id'):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width=title_width)
        self.text = text
        self.color = color
        self.link = link
        self.icon = icon
        self.size = size

    def get_html(self, request, instance):
        value = get_value(instance, self.field)
        try:
            link = reverse(self.link, args=(
                value,
            ))
        except:
            link = self.link

        return link_button(self.text, self.color, link, self.icon, self.size)


class BootstrapButtonSetColumn(DataTableColumn):
    def __init__(self, buttons, field='id', title='', title_class=None, title_width="20px", ):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width)
        self.buttons = buttons

    def get_html(self, request, instance):
        data = []
        for button in self.buttons:
            text = button.get('text', '')
            color = button.get('color', '')
            link = button.get('link', '')
            icon = button.get('icon', '')
            size = button.get('size', '')

            field = button.get('field', self.field)
            value = getattr(instance, field)
            try:
                link = reverse(link, args=(value, ))
            except:
                pass
            data.append({
                'link': link,
                'text': text,
                'color': color,
                'icon': icon,
                'size': size
            })

        return link_button_set(data)


class LinkDataTableColumn(DataTableColumn):
    def __init__(self, text, link, title_width="20px", title='', field='id', title_class=None):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width)
        self.text = text
        self.link = link

    def get_html(self, request, instance):
        value = getattr(instance, self.field)
        try:
            link = reverse(self.link, args=(
                value,
            ))
        except:
            link = self.link

        return generate_code('a', {
            'href': link
        }, self.text)


class EmailDataTableColumn(DataTableColumn):
    def __init__(self, field, title, searchable, sortable, title_class=None, title_width=None):
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width)

    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return generate_code('a', {
            'href': 'mailto:' + value
        }, value)


class DateDataTableColumn(DataTableColumn):
    def __init__(self, field, title, searchable, sortable, date_format=None, title_class=None, title_width=None):
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width)
        self.date_format = date_format

    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return date(value, self.date_format)
