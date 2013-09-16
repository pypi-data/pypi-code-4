from django.utils.translation import ugettext as _


def trans(key):
    """
    Wraps string with special prefix and suffix
    """
    prefix = '{{__'
    suffix = '__}}'
    return _(prefix + key + suffix)


def trans2(key):
    """
    Wraps string with onesky's tag
    """
    tag = 'os-p'
    return _('<%s key="%s">%s</%s>' % (tag, key, _(key), tag))