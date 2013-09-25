from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_relinking.content_types import get_object


class Link(models.Model):

    TARGET_CHOICES = [
        (0, "_self"),
        (1, "_blank")
    ]

    keys = models.TextField(
        verbose_name=_(u"keys for replacing"),
        help_text=_(u"One key per line. The key can include many words and different characters")
    )

    content_type = models.CharField(
        verbose_name=_(u"content type"),
        max_length=255,
        default=None,
        null=True,
        blank=True,
        choices=[]
    )
    object_pk = models.CharField(
        verbose_name=_(u"object"),
        max_length=255,
        default=None,
        null=True,
        blank=True
    )

    direct_link = models.CharField(
        verbose_name=_(u"direct link"),
        max_length=255,
        default=None,
        null=True,
        blank=True,
        help_text=_(u"If you set this field, 'content type' and 'object primary key' will not be used")
    )

    target = models.IntegerField(
        verbose_name=_(u"link target"),
        default=0,
        null=False,
        blank=False,
        choices=[(0, u"_self"), (1, u"_blank")]
    )

    priority = models.IntegerField(
        verbose_name=_(u"priority"),
        default=0,
        null=False,
        blank=False
    )

    @property
    def keys_list(self):
        return [ob.strip() for ob in self.keys.split("\n") if ob.strip()]

    @property
    def url(self):
        if self.direct_link:
            return self.direct_link
        return get_object(self.content_type, self.object_pk).get_absolute_url()

    def __unicode__(self):
        return self.keys

    class Meta(object):
        ordering = ["priority"]
        verbose_name = _(u"link")
        verbose_name_plural = _(u"links")
