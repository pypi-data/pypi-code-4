from django_helpers.helpers.views import render_to_string
from django_helpers.apps.static_manager import jQueryURL, BootstrapURL

__author__ = 'ajumell'

from . import Menu


class BootstrapPillMenu(Menu):
    nav_type = 'pills'
    stacked = False

    has_js = True

    def __init__(self, context, items=None):
        Menu.__init__(self, context, items)
        self.js_files = [jQueryURL, BootstrapURL, 'js/jquery.django.ajax.js']

    def render_menu_start(self, level):
        if level is 0:
            classes = self.menu_classes[:]
            classes.insert(0, 'nav')
            classes.insert(1, 'nav-' + self.nav_type)

            if self.stacked:
                classes.insert(2, 'nav-stacked')

            return '<ul class="%s">' % ' '.join(classes)
        else:
            return '<ul class="dropdown-menu">'

    def get_template(self, level, has_sub_menu, decedent_current, is_current):
        if level == 0:
            if has_sub_menu:
                return 'menu/bootstrap-nav-with-drop-down.html'
            else:
                return 'menu/bootstrap-nav.html'

        if level > 0:
            if has_sub_menu:
                return 'menu/bootstrap-drop-down-item-with-sub.html'
            else:
                return 'menu/bootstrap-drop-down-item.html'

    def render_js(self):
        op = render_to_string('menu/bootstrap-dropdown.js', {
            'menu_id': self.menu_id,
            'ajax': self.ajax
        })
        return op