from django.utils.translation import ugettext as _


def trans(msg):
    """
    Wraps string with onesky's tag
    """
    tag = 'os-p'
    return _('<%s key="%s">%s</%s>' % (tag, msg, msg, tag))


def trans2(msg):
    """
    Wraps string with special prefix and suffix
    """
    prefix = '{{__'
    suffix = '__}}'
    return _(prefix + msg + suffix)