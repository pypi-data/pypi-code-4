from django.db import models
from csat.acquisition.models import DataCollectorConfig
from django.utils.translation import ugettext_lazy as _


class PipermailConfig(DataCollectorConfig):
    EVERYBODY_TO_EVERYBODY = 0
    EVERYBODY_TO_AUTHOR = 1
    LINK_CHOICES = (
        (EVERYBODY_TO_EVERYBODY, _('Everybody to everybody')),
        (EVERYBODY_TO_AUTHOR, _('Everybody to thread author')),
    )

    base_url = models.URLField(_('Base archives URL'))
    link_mode = models.PositiveSmallIntegerField(_('Linking mode'),
                                                 choices=LINK_CHOICES,
                                                 default=EVERYBODY_TO_AUTHOR)
