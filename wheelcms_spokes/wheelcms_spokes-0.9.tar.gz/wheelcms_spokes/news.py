from django.db import models
from django import forms

from django.utils.html import strip_tags
from django.utils.text import Truncator

from tinymce.widgets import TinyMCE

from wheelcms_axle.content import type_registry, Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke
from wheelcms_axle.forms import formfactory


class NewsBase(Content):
    """ A news object """
    class Meta:
        abstract = True

    intro = models.TextField(blank=False)
    body = models.TextField(blank=False)

class News(NewsBase):
    pass

class NewsForm(formfactory(News)):
    body = forms.CharField(widget=TinyMCE(), required=False)

class NewsType(Spoke):
    model = News
    form = NewsForm

    title = "A simple News item"

    type_icon = icon = "news.png"

    def index_description(self):
        """ truncate body text if no explicit description available """
        return self.description()

    def description(self):
        """ truncate body text if no explicit description available """
        if self.instance.intro:
            return self.instance.intro

        if self.instance.description:
            return self.instance.description

        return Truncator(strip_tags(self.instance.body)).words(50,
                         truncate=" ...")
template_registry.register(NewsType, "wheelcms_spokes/news_view.html", "Basic News view", default=True)
type_registry.register(NewsType)
