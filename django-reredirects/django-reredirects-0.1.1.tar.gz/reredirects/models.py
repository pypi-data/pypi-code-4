from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Redirect(models.Model):
    old_path = models.CharField(_('redirect from'), max_length=400, db_index=True,
        unique=True, help_text=_("This should be an absolute path, excluding the domain name. Regex can be included. Example: '/events/search/'."))
    new_path = models.CharField(_('redirect to'), max_length=400, blank=True,
        help_text=_("This can be either an absolute path (as above) or a full URL starting with 'http://'. For regex patterns, use $1, $2 for matches"))

    class Meta:
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
        ordering = ('old_path',)

    def __str__(self):
        return "%s ---> %s" % (self.old_path, self.new_path)
