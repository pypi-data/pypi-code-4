from types import StringTypes
from django.core.urlresolvers import reverse, resolve
from django.template import RequestContext, Parser, resolve_variable
from django.utils.safestring import mark_safe

from django_helpers.helpers.views import render_to_string
from django_helpers.apps.static_manager import jQueryURL

from exceptions import InvalidContextException, MenuIDNotFoundException, MultipleMenuWithSameIDException

from helpers import *

__author__ = 'ajumell'

__all__ = ('Menu', 'register', 'has_menu', 'get_menu', 'menu_item')

_REGISTERED_MENU = {}


class Menu(object):
    menu_classes = []
    items = []
    has_js = True
    menu_id = None
    highlight_current = True
    ajax = False

    def __init__(self, context, items=None):

        if not isinstance(context, RequestContext):
            InvalidContextException()

        if self.menu_id is None:
            MenuIDNotFoundException()

        request = resolve_variable('request', context)
        self.current_url = resolve(request.path_info).url_name
        self.path = request.get_full_path()
        self.current = False
        self.current_level = None

        self.items = self.items[:]

        if items is not None and self.items is None:
            self.items = items

        self.context = context
        self.parser = Parser('')
        self.user = resolve_variable('user', context)

        self.js_files = [jQueryURL, 'js/superfish.min.js', 'js/jquery.django.ajax.js']

    def format_text(self, text, params):
        context = self.context
        args = []
        for param in params:
            default = None
            if type(param) in (tuple, list):
                param, default = param
            try:
                op = resolve_variable(param, context)
            except:
                op = default if default is not None else param
            args.append(op)
        return text % tuple(args)

    def should_render(self, item):
        user = self.user
        perms = item.get('perms')
        need_auth = item.get('need_auth')
        need_guest = item.get('need_guest')

        if need_auth and not user.is_authenticated():
            return False

        if need_guest and not user.is_anonymous():
            return False

        has_perm = True
        if perms is not None:
            for perm in perms:
                has_perm = has_perm and user.has_perm(perm)
                if not has_perm:
                    return False
        return has_perm

    def get_template(self, level, has_sub_menu, decedent_current, is_current):
        return 'menu/simple-item.html'

    def extra_item_context_vars(self, item, level, d):
        pass

    def can_highlight(self, item, current_link, no_reverse, decedent_current):
        pass

    def render_item(self, item, level):
        text = item.get('text')
        link_name = item.get('link')

        text_params = item.get('text_params')
        if text_params is not None:
            text = self.format_text(text, text_params)

        no_reverse = item.get('no_reverse', False)

        if not no_reverse:
            link = reverse(link_name, args=item.get('link_args'), kwargs=item.get('link_kwargs'))
        else:
            link = link_name

        if link == self.path:
            self.current = True
            self.current_level = level

        sub_menu_html = ''
        sub_menu_items = item.get('sub_menu', None)
        has_sub_menu = False

        if sub_menu_items is not None:

            if hasattr(sub_menu_items, '__call__'):
                sub_menu_items = sub_menu_items()

            sub_menu = self.render_list(sub_menu_items, level + 1)
            has_sub_menu = sub_menu is not ''
            if has_sub_menu:
                sub_menu_html += self.render_menu_start(level + 1)
                sub_menu_html += sub_menu
                sub_menu_html += self.render_menu_end(level + 1)

        is_current = self.current and self.current_level == level and link == self.path
        decedent_current = self.current and self.current_level > level

        # Can Highlight
        highlighted = is_current or decedent_current
        extra_highlight_options = item.get('highlight-names', None)
        if type(extra_highlight_options) in StringTypes:
            extra_highlight_options = [extra_highlight_options]

        if type(extra_highlight_options) in (tuple, list):
            highlighted = highlighted or self.current_url in extra_highlight_options

        d = {
            'url': link,
            'text': text,
            'is_current': is_current,
            'decedent_current': decedent_current,
            'can_highlight': highlighted,
            'has_sub_menu': has_sub_menu,
            'sub_menu': mark_safe(sub_menu_html)
        }

        self.extra_item_context_vars(item, level, d)

        if level == 0:
            self.current = False
            self.current_level = None

        return render_to_string(self.get_template(level, has_sub_menu, decedent_current, is_current), d)

    def render_list(self, items, level):
        op = []
        for item in items:
            if self.should_render(item):
                op.append(self.render_item(item, level))
        return '\n'.join(op)

    def render_menu_start(self, level):
        if level is 0:
            classes = self.menu_classes[:]
            return '<ul class="sf-menu %s" id="%s">' % (' '.join(classes), self.menu_id)
        else:
            return '<ul>'

    # noinspection PyUnusedLocal
    def render_menu_end(self, level):
        return '</ul>'

    def render(self):
        op = ''

        op += self.render_menu_start(0)
        op += self.render_list(self.items, 0)
        op += self.render_menu_end(0)

        return op

    def render_js(self):
        op = render_to_string('menu/super-fish.js', {
            'menu_id': self.menu_id,
            'ajax': self.ajax
        })
        return op


def register(cls):
    menu_id = getattr(cls, 'menu_id', None)

    if menu_id is None:
        raise MenuIDNotFoundException()

    if menu_id in _REGISTERED_MENU:
        if _REGISTERED_MENU[menu_id] != cls:
            raise MultipleMenuWithSameIDException()
    else:
        _REGISTERED_MENU[menu_id] = cls
    return cls


def has_menu(name):
    return name in _REGISTERED_MENU


def get_menu(name):
    return _REGISTERED_MENU[name]