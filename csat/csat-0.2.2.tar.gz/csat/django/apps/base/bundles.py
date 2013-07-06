from django_assets import Bundle, register
from django.conf import settings


if getattr(settings, 'ASSETS_VERSIONS', True):
    postfix = '-%(version)s'
else:
    postfix = ''


if settings.DEBUG:
    jsfilters = []
else:
    jsfilters = ['jsmin']


def make_bundle(name, files, **kwargs):
    register_flag = kwargs.pop('register', True)
    bundle = Bundle(*files, **kwargs)
    if register_flag:
        register(name, bundle)
    return bundle


def make_css_bundle(name, files, **kwargs):
    if 'output' not in kwargs:
        kwargs['output'] = 'styles/{}{}.css'.format(name, postfix)
    return make_bundle('{}_css'.format(name), files, **kwargs)


def make_js_bundle(name, files, **kwargs):
    if 'output' not in kwargs:
        kwargs['output'] = 'scripts/{}{}.js'.format(name, postfix)
    return make_bundle('{}_js'.format(name), files, **kwargs)


def sass(path):
    return 'sass/{}.sass'.format(path)


def coffee(path):
    return 'coffeescripts/{}.coffee'.format(path)
