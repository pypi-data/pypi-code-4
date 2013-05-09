# coding: utf-8
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import SyntaxHighlighter
from django.utils.translation import ugettext as _
from django.conf import settings

class SyntaxHighlighterPlugin(CMSPluginBase):
    model = SyntaxHighlighter
    name = _("Syntax Highlighter")
    render_template = "cmsplugin_syntax_highlight/plain.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({'instance' : instance})
        context.update({'syntax_highlighter': settings.SYNTAX_HIGHLIGHTER})
        self.render_template = instance.template
        return context

    def icon_src(self, instance):
        return settings.STATIC_URL + u"cmsplugin_syntax_highlight/icon.png"

plugin_pool.register_plugin(SyntaxHighlighterPlugin)
