# coding=utf-8
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date
from django.utils.dateparse import parse_datetime, parse_date
from columns import DataTableColumn, get_value
from django_helpers.utils.bootstrap import link_button, generate_code, link_button_set


class BootstrapButtonColumn(DataTableColumn):
    def __init__(self, text, color, link, icon='', size=None, title_class=None, title_width="85px", title='', field='id'):
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
    def __init__(self, buttons, field='id', title='', title_class=None, title_width="auto", ):
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


class BootstrapInfoButton(BootstrapButtonColumn):
    def __init__(self, text, link, icon='', size=None, title_class=None, title_width="85px", title='', field='id'):
        BootstrapButtonColumn.__init__(text, 'info', link, icon, size, title_class, title_width, title, field)


class BootstrapSuccessButton(BootstrapButtonColumn):
    def __init__(self, text, link, icon='', size=None, title_class=None, title_width="85px", title='', field='id'):
        BootstrapButtonColumn.__init__(text, 'success', link, icon, size, title_class, title_width, title, field)


class BootstrapErrorButton(BootstrapButtonColumn):
    def __init__(self, text, link, icon='', size=None, title_class=None, title_width="85px", title='', field='id'):
        BootstrapButtonColumn.__init__(text, 'error', link, icon, size, title_class, title_width, title, field)


class BootstrapWarningButton(BootstrapButtonColumn):
    def __init__(self, text, link, icon='', size=None, title_class=None, title_width="85px", title='', field='id'):
        BootstrapButtonColumn.__init__(text, 'warning', link, icon, size, title_class, title_width, title, field)


class BootstrapPrimaryButton(BootstrapButtonColumn):
    def __init__(self, text, link, icon='', size=None, title_class=None, title_width="85px", title='', field='id'):
        BootstrapButtonColumn.__init__(text, 'primary', link, icon, size, title_class, title_width, title, field)


class StaticLinkDataTableColumn(DataTableColumn):
    def __init__(self, text, link, title_width="20px", title='', field='id', title_class=None, search_lookup='contains'):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width, search_lookup=search_lookup)
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


class LinkDataTableColumn(DataTableColumn):
    def __init__(self, field, link, title, searchable, sortable, link_field=None, title_class=None, title_width=None, search_lookup='contains', format_expression=None):
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width, search_lookup=search_lookup, format_expression=format_expression)
        self.link = link
        self.link_field = link_field

    def get_fields(self):
        field = self.field
        link_field = self.link_field
        if field == link_field:
            return field
        return field, link_field

    def get_html(self, request, instance):
        value = get_value(instance, self.field, self.format_expression)
        link_arg = get_value(instance, self.link_field or self.field)

        try:
            link = reverse(self.link, args=(
                link_arg,
            ))
        except:
            link = self.link

        return generate_code('a', {
            'href': link
        }, value)


class EmailDataTableColumn(DataTableColumn):
    def __init__(self, field, title, searchable, sortable, title_class=None, title_width=None,
                 annotate=None, search_lookup='contains', format_expression=None):
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width, False, annotate, search_lookup, format_expression)

    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return generate_code('a', {
            'href': 'mailto:' + value
        }, value)


class DateDataTableColumn(DataTableColumn):
    def __init__(self, field, title, searchable, sortable, date_format=None, title_class=None, title_width=None,
                 editable=False, annotate=None, search_lookup='contains', format_expression=None):
        DataTableColumn.__init__(self, field, title, searchable, sortable, title_class, title_width, editable, annotate, search_lookup, format_expression)
        self.date_format = date_format

    def get_html(self, request, instance):
        value = get_value(instance, self.field)
        if self.annotate is not None:
            str_value = value
            value = parse_date(str_value)
            if value is None:
                value = parse_datetime(str_value)
        value = date(value, self.date_format)
        if self.format_expression is not None:
            value = self.format_expression % value
        return value


class CheckboxColoum(DataTableColumn):
    def __init__(self, title_class=None, name=None, extra_classes=None, title_width="25px", title='', field='id'):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width)
        # self.title = mark_safe('<input type="checkbox">')
        self.name = name
        self.extra_classes = extra_classes

    def get_html(self, request, instance):
        attrs = {
            'type': 'checkbox',
            'class': self.extra_classes,
            'name': self.name,
            'value': get_value(instance, self.field)
        }
        return generate_code('input', attrs, self_closing=True)


class ImageField(DataTableColumn):
    def __init__(self, field, title='', convert_url=True, title_class=None, extra_classes=None, title_width="25px"):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width)
        self.convert_url = convert_url
        self.extra_classes = extra_classes

    def get_html(self, request, instance):
        obj = get_value(instance, self.field)
        try:
            url = obj.thumbnail
        except:
            url = obj.url
        attrs = {
            'class': self.extra_classes,
            'src': url
        }
        return generate_code('img', attrs, self_closing=True)


class BooleanImageField(DataTableColumn):
    def __init__(self, field, yes_image, no_image, title='', title_class=None, extra_classes=None, title_width="25px"):
        DataTableColumn.__init__(self, field, title, False, False, title_class, title_width)
        self.extra_classes = extra_classes
        self.yes_image = yes_image
        self.no_image = no_image

    def get_html(self, request, instance):
        obj = get_value(instance, self.field)
        url = self.yes_image if obj else self.no_image
        attrs = {
            'class': self.extra_classes,
            'src': url
        }
        return generate_code('img', attrs, self_closing=True)
