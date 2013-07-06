from django.db import models
from csat.acquisition.models import DataCollectorConfig
from django.utils.translation import ugettext_lazy as _


class Config(DataCollectorConfig):
    repo_url = models.CharField(_('Repository URL'), max_length=255)
    revspec = models.CharField(_('Revision specifier'), max_length=255)
    package = models.CharField(_('Package directory'), max_length=63)
    keep_history = models.BooleanField(_('Keep history'), default=False)
