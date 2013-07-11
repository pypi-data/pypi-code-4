# -*- coding: utf-8 -*-

from floppyforms.widgets import TextInput
from django.forms import Media
from django.core.urlresolvers import reverse
from djaloha import settings

class AlohaInput(TextInput):
    """
    Text widget with aloha html editor
    requires floppyforms to be installed
    """

    template_name = 'djaloha/alohainput.html'

    def __init__(self, *args, **kwargs):
        kwargs.pop('text_color_plugin', None) # for compatibility with previous versions
        self.aloha_plugins = kwargs.pop('aloha_plugins', None)
        self.extra_aloha_plugins = kwargs.pop('extra_aloha_plugins', None)
        self.aloha_init_url = kwargs.pop('aloha_init_url', None)
        super(AlohaInput, self).__init__(*args, **kwargs)

    def _get_media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        """

        try:
            aloha_init_url = self.aloha_init_url or settings.init_url()
            aloha_version = settings.aloha_version()

            aloha_plugins = self.aloha_plugins
            if not aloha_plugins:
                aloha_plugins = settings.plugins()
            
            if self.extra_aloha_plugins:
                aloha_plugins = tuple(aloha_plugins) + tuple(self.extra_aloha_plugins)

            css = {
                'all': (
                    "{0}/css/aloha.css".format(aloha_version),
                )
            }

            js = []

            if not settings.skip_jquery():
                js.append(settings.jquery_version())

            ##Why?
            if aloha_version.startswith('aloha.0.22.'):
                js.append("{0}/lib/require.js".format(aloha_version))

            js.append(aloha_init_url)
            js.append(u'{0}/lib/aloha.js" data-aloha-plugins="{1}'.format(aloha_version, u",".join(aloha_plugins)))
            js.append('djaloha/js/djaloha-init.js')
            
            return Media(css=css, js=js)
        except Exception, msg:
            print '## AlohaInput._get_media Error ', msg

    media = property(_get_media)
