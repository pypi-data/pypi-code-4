import pkg_resources
from django.template import Library
from django.conf import settings


register = Library()


@register.inclusion_tag('djinn_core/snippets/css.html')
def list_plugin_css(static_url):

    css = []

    for entrypoint in pkg_resources.iter_entry_points(group="djinn.app",
                                                      name="css"):        
        css.extend(entrypoint.load()())

    return {"plugin_css": css, "STATIC_URL": static_url}


@register.inclusion_tag('djinn_core/snippets/js.html')
def list_plugin_js(static_url):

    js = []

    for entrypoint in pkg_resources.iter_entry_points(group="djinn.app",
                                                      name="js"):
        js.extend(entrypoint.load()())

    return {"plugin_js": js, "STATIC_URL": static_url}
