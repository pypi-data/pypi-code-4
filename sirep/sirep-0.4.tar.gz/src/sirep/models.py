from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from sirep.conf import get_setting

SHOW_ADMIN_TEST_MODEL_DEMO = get_setting('SHOW_ADMIN_TEST_MODEL_DEMO')

class TestModel(models.Model):
    """
    Test model for making a report.
    """
    title = models.CharField(_("Title"), max_length=50, blank=False, null=False)
    counter = models.PositiveIntegerField(_("Counter"), blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True)
    date_published = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Sirep test model")
        verbose_name_plural = _("Sirep test models")

    def __unicode__(self):
        return self.title