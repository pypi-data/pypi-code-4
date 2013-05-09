import threading
from django.db import models
from cms.models.pluginmodel import CMSPlugin
import utils

localdata = threading.local()
localdata.TEMPLATE_CHOICES = utils.autodiscover_templates('cmsplugin_syntax_highlight')
TEMPLATE_CHOICES = localdata.TEMPLATE_CHOICES

class SyntaxHighlighter(CMSPlugin):
    template = models.CharField(max_length=255,
                                choices=TEMPLATE_CHOICES)
    content = models.TextField()

    def __str__(self):
        return "highlighter_" + str(self.id)

    def __unicode__(self):
        return "highlighter_" + str(self.id)
