import json
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


def trailing_slash():
    if getattr(settings, 'MISSING_TRAILING_SLASH', False):
        return '/'
    else:
        return '/?'


def json_parse(content):
    return json.dumps(content, cls=DjangoJSONEncoder)


def json_loads(content):
    return json.loads(content)