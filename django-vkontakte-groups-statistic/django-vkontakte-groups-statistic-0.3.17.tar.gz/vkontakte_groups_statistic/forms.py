# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from vkontakte_groups.forms import GroupImportForm
from models import Group
from datetime import datetime, timedelta

class GroupImportStatisticForm(GroupImportForm):
    def save(self, *args, **kwargs):
        group = super(GroupImportStatisticForm, self).save(*args, **kwargs)
        group.fetch_statistic()
        return group