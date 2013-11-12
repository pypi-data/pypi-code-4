from django.db import models
from django import forms

from django.utils.html import strip_tags
from django.utils.text import Truncator

from wheelcms_axle.content import type_registry
from wheelcms_axle.content import Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke, indexfactory, SpokeCharField
from wheelcms_axle.node import Node
from wheelcms_axle.node import node_proxy_factory

from wheelcms_axle.forms import formfactory
from wheelcms_axle import access
from wheelcms_axle.utils import get_active_language

from wheelcms_axle.forms import TinyMCE
from tinymce.models import HTMLField

##
## Either HTMLField or TinyMCE widget. But a demonstration on how to alter
## a Spoke's form is also nice to have.

class PageBase(Content):
    """ A simple page object """

    class Meta:
        abstract = True

    body = models.TextField(blank=False)
    # body = HTMLField(blank=False)

class Page(PageBase):
    pass

class PageForm(formfactory(Page)):
    body = forms.CharField(widget=TinyMCE(), required=False)


class PageType(Spoke):
    document_fields = Spoke.document_fields + ("body", )

    model = Page
    title = "A page"
    form = PageForm

    @property
    def icon(self):
        if self.instance.node.children().exists():
            return "folder_page.png"
        return "page.png"

    def index_description(self):
        """ truncate body text if no explicit description available """
        return self.description()

    def description(self):
        """ truncate body text if no explicit description available """
        if self.instance.description:
            return self.instance.description

        return Truncator(strip_tags(self.instance.body)).words(50,
                         truncate=" ...")

    @classmethod
    def index(cls):
        class PageIndex(indexfactory(cls)):
            description = SpokeCharField(spoke=cls,
                                         stored=True, indexed=False,
                                         model_attr="index_description")

        return PageIndex

    def context(self, handler, request, node):
        ctx = super(PageType, self).context(handler, request, node)
        wpm = 180  # avg adult for monitor
        # XXX NOTTESTED
        ctx['reading_minutes'] = (len(strip_tags(self.instance.body).split())/wpm) + 1
        return ctx

def contentlisting_context(handler, request, node):
    language = get_active_language(request)

    q = node_proxy_factory(Node, language).objects.children(node).filter(contentbase__language=language).order_by("position")

    if not access.has_access(request.user, node):
        q = q.public()

    return dict(contents=q)

type_registry.register(PageType)
template_registry.register(PageType, "wheelcms_spokes/page_view.html",
                           "Basic Page view", default=True)
template_registry.register(PageType, "wheelcms_spokes/page_contents.html",
                           "Contents Listing", default=False,
                           context=contentlisting_context)
