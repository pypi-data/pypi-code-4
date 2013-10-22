from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic import PolymorphicModel


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
    slug = models.CharField(_('Slug'), max_length=255, blank=True)
    prefix = models.CharField(_('Prefix'), max_length=255, blank=True)
    enabled = models.BooleanField(_('Enabled'), default=False,
                                  help_text=_('Enable this theme (and disable the current, if enabled).'))
    debug = models.BooleanField(_('Debug'), default=False,
                                help_text=_('Reload theme on every request (vs. reload on changing themes).'))

    path = models.CharField(_('Path'), blank=True, null=True, max_length=255)
    url = models.CharField(_('Url'), blank=True, null=True, max_length=255)
    builtin = models.BooleanField(_('Built-in'), default=False)

    rules = models.ForeignKey(Rule, related_name='themes', blank=True, null=True)

    def __unicode__(self):
        return self.name
