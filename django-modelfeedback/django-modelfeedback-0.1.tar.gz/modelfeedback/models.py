from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Feedback(models.Model):
    RATING_CHOICES = (
        (5, _('Very Satisfied')),
        (4, _('Satisfied')),
        (3, _('Neither Satisfied nor Dissatisfied')),
        (2, _('Dissatisfied')),
        (1, _('Very Dissatisfied')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField(_('object id'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    message = models.TextField(_('message'), blank=True)
    rating = models.PositiveSmallIntegerField(_('rating'),
                                              choices=RATING_CHOICES)

    @models.permalink
    def get_absolute_url(self):
        return ('detail', (self.id,))

    @classmethod
    def create(cls, user, obj):
        return cls(user=user,
                   object_id=obj.id,
                   content_type=ContentType.objects.get_for_model(obj),
                   rating=1)

    def unique_error_message(self, *args, **kwargs):
        return _('You have already given this feedback.')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
