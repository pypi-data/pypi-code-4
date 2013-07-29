from django.db import models
from csat.acquisition.models import DataCollectorConfig
from django.utils.translation import ugettext_lazy as _


class RandomConfig(DataCollectorConfig):
    domains = models.PositiveIntegerField(_('Domains'))
    nodes = models.PositiveIntegerField(_('Nodes'))
    edges = models.PositiveIntegerField(_('Edges'))
    ratio = models.FloatField(_('Intra-/Inter-layer edges ratio'), blank=True,
                              null=True)
    seed = models.IntegerField(_('PRNG seed'), blank=True, null=True)
