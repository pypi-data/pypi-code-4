from django.db import models
from cms.models import CMSPlugin
from djangocms_text_ckeditor.fields import HTMLField


class Carousel(CMSPlugin):
    name = models.CharField(max_length=250)

    def copy_relations(self, oldinstance):
        for slide in oldinstance.slide_set.all():
            slide.pk = None
            slide.save()
            self.slide_set.add(slide)

    def __unicode__(self):
        return self.name


class Slide(models.Model):
    image = models.ImageField(upload_to="slides")
    title = models.CharField(max_length=250)
    text = HTMLField(blank=True)
    carousel = models.ForeignKey(Carousel)
