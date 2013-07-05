from django.db import models
from csat.acquisition.models import DataCollectorConfig
from django.utils.translation import ugettext_lazy as _

from . import graphs


class ExamplesConfig(DataCollectorConfig):
    GRAPH_CHOICES = [(g.key, g.description) for g in graphs.get_graphs()]

    example = models.CharField(_('Example'), choices=GRAPH_CHOICES, max_length=255)
