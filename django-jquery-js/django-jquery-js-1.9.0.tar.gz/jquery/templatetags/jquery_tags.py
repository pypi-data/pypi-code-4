from django.conf import settings
from django.forms.widgets import flatatt
from django.template import Library

from jquery.utils import jquery_path

register = Library()


@register.simple_tag
def jquery_script():
    return '<script{0}></script>'.format(flatattr({
        'type': 'text/javascript',
        'src': settings.MEDIA_URL + jquery_path,
    }))
