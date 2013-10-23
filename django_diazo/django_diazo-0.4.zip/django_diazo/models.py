import os
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic import PolymorphicModel
from django.db.models import Max


class Rule(PolymorphicModel):
    name = models.CharField(_('Name'), max_length=255)
    root = models.BooleanField(_('Root'), default=False,
                               help_text=_('This rule can be used as root for a theme transformation.'))

    def __unicode__(self):
        return self.name

    def serialize(self):
        pass


class SingleRule(Rule):
    rule = models.TextField(_('Rule'))

    def serialize(self):
        return self.rule


class CompoundRule(Rule):
    prefix = models.TextField(_('Suffix'))
    rules = models.ManyToManyField(Rule, related_name='compound_rule', blank=True)
    suffix = models.TextField(_('Suffix'))

    def serialize(self):
        return self.prefix + '\n'.join([r.serialize() for r in self.rules.all()]) + self.suffix


class Theme(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=255)
    prefix = models.CharField(_('Prefix'), max_length=255, blank=True)
    enabled = models.BooleanField(_('Enabled'), default=False,
                                  help_text=_('Enable this theme (and disable the current, if enabled).'))
    debug = models.BooleanField(_('Debug'), default=False,
                                help_text=_('Reload theme on every request (vs. reload on changing themes).'))

    sort = models.IntegerField(_('sort'), blank=True, null=True,
                               help_text=_('The order in which the themes will be loaded (the lower, the earlier).'))
    path = models.CharField(_('Path'), blank=True, null=True, max_length=255)
    url = models.CharField(_('Url'), blank=True, null=True, max_length=255)
    builtin = models.BooleanField(_('Built-in'), default=False)

    rules = models.ForeignKey(Rule, related_name='themes', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.sort:
            max = Theme.objects.aggregate(Max('sort'))['sort__max']
            self.sort = (max or 0) + 1
        super(Theme, self).save(*args, **kwargs)

    def available(self, request):
        try:
            ua = request.META['HTTP_USER_AGENT']
        except:
            return False
        for x in self.useragent_strings.order_by('sort'):
            if x.pattern in ua:
                return x.allow == 'allow'
        return True

    def theme_path(self, include_prefix=True):
        if self.builtin:
            return self.path
        else:
            return os.path.join(
                format(settings.MEDIA_ROOT), 'themes', str(self.pk),
                self.prefix if include_prefix else '')

    def theme_url(self):
        if self.builtin:
            return self.url
        else:
            return '/'.join([
                format(settings.MEDIA_URL) + 'themes', str(self.pk),
                self.prefix])


class ThemeUserAgent(models.Model):
    theme = models.ForeignKey(Theme, related_name='useragent_strings')
    pattern = models.CharField(
        verbose_name=_('Pattern'),
        help_text=_('When pattern exists in HTTP_USER_AGENT'),
        max_length=255)
    allow = models.CharField(
        verbose_name=_('Allow or deny'),
        choices=[('allow', _('Allow')), ('deny', _('Deny'))],
        max_length=10,
        help_text=_('Allow or deny loading this theme when the pattern matches.'))
    sort = models.IntegerField(_('sort'), blank=True, null=True,
                               help_text=_('The order in which the patterns will be matched (the lower, the earlier).'))

    def __unicode__(self):
        return ' '.join([self.allow, self.pattern])

    def save(self, *args, **kwargs):
        if not self.sort:
            max = self.theme.useragent_strings.aggregate(Max('sort'))['sort__max']
            self.sort = (max or 0) + 1
        super(ThemeUserAgent, self).save(*args, **kwargs)

