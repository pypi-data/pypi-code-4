from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.template.defaultfilters import slugify


class Article(CMSPlugin):
    """
    Define the attributes of an article object.
    """
    title = models.CharField(max_length=48)
    slug = models.SlugField(editable=False)
    description = models.CharField(max_length=64, blank=True)
    body = models.TextField(help_text='Must be html. Use text plugin if this is a problem.')

    """
    Override the save method to auto-slug the title.
    """
    def save(self, *args, **kwargs):
        if not self.slug:
            # Set slug only if new to keep from breaking links.
            self.slug = slugify(self.title)

        super(Article, self).save(*args, **kwargs)
