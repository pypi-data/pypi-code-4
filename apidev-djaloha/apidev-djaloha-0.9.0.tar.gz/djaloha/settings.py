# -*- coding: utf-8 -*-

from django.conf import settings as project_settings
from django.core.urlresolvers import reverse

def aloha_version():
    return getattr(project_settings, 'DJALOHA_ALOHA_VERSION', "aloha.0.22.6")
    
def init_js_template():
    return getattr(project_settings, 'DJALOHA_INIT_JS_TEMPLATE', "djaloha/aloha_init.js")

def init_url():
    return getattr(project_settings, 'DJALOHA_INIT_URL', None) or reverse('aloha_init')

def plugins():
    plugins = getattr(project_settings, 'DJALOHA_PLUGINS', None)
    if not plugins:
        plugins = (
            "common/format",
            #"custom/format",
            "common/highlighteditables",
            "common/list",
            "common/link",
            "common/undo",
            "common/paste",
            "common/commands",
            "common/contenthandler",
            "common/image",
            #"custom/zimage",
            "common/align",
            #"extra/attributes",
            "common/characterpicker",
            #"common/abbr",
            "common/horizontalruler",
            "common/table",
        )
    return plugins
    
def skip_jquery():
    return getattr(project_settings, 'DJALOHA_SKIP_JQUERY', False)
    
def jquery_version():
    if project_settings.DEBUG:
        return getattr(project_settings, 'DJALOHA_JQUERY', "js/jquery-1.7.2.js")
    else:
        return getattr(project_settings, 'DJALOHA_JQUERY', "js/jquery-1.7.2.js")
    
def jquery_no_conflict():
    return getattr(project_settings, 'DJALOHA_JQUERY_NO_CONFLICT', True)
    
def link_models():
    return getattr(project_settings, 'DJALOHA_LINK_MODELS', ())
    
def sidebar_disabled():
    return getattr(project_settings, 'DJALOHA_SIDEBAR_DISABLED', True)
    
def css_classes():
    return getattr(project_settings, 'DJALOHA_CSS_CLASSES', ())
    
def resize_disabled():
    return getattr(project_settings, 'DJALOHA_RESIZE_DISABLED', False)
