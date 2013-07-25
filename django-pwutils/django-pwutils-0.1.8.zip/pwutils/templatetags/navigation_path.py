from django.template import Library

from  pwutils.utils import NavItem

register = Library()


@register.inclusion_tag('navigation_path.html', takes_context=True)
def navigation_path(context, obj=None):
    obj = obj or context.get('nav_path')

    try:
        len(obj)
    except TypeError:
        try:
            parts = obj.get_navigation_path()
        except AttributeError:
            parts = list()
    else:
        parts = obj

    # make last not active
    if parts:
        last = parts[-1]
        try:
            title = last.title
        except AttributeError:
            try:
                title = last.name
            except AttributeError:
                title = unicode(last)

        parts[-1] = NavItem(title=title)

    return {'parts': parts}
