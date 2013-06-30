#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Signals for config variables and permissions to builtin groups.
"""

from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.translation import ugettext as _, ugettext_lazy

from openslides.config.api import ConfigVariable, ConfigPage
from openslides.config.signals import config_signal
from openslides.core.signals import post_database_setup
from openslides.participant.api import get_registered_group
from openslides.participant.models import Group


@receiver(config_signal, dispatch_uid='setup_openslides_topicvoting_config')
def setup_openslides_topicvoting_config(sender, **kwargs):
    """
    Config variables:
        * openslides_topicvoting_posts
        * openslides_topicvoting_ballotpaper_title
        * openslides_topicvoting_ballotpaper_text
    """
    posts = ConfigVariable(
        name='openslides_topicvoting_posts',
        default_value=8,
        form_field=forms.IntegerField(
            label=ugettext_lazy('Number of topics to be elected'),
            min_value=1,
            help_text=ugettext_lazy('The winning topics are highlighted in the result table.')))

    ballotpaper_title = ConfigVariable(
        name='openslides_topicvoting_ballotpaper_title',
        default_value='Wahlen der Themenabende',
        form_field=forms.CharField(
            required=False,
            label=ugettext_lazy('Title of the ballot paper')))

    ballotpaper_text = ConfigVariable(
        name='openslides_topicvoting_ballotpaper_text',
        default_value='Sie haben 5 Stimmen. Ein Thema kann bis zu 5 Stimmen '
                      'erhalten. Schreiben Sie die Zahl vor das jeweilige Thema.',
        form_field=forms.CharField(
            widget=forms.Textarea(),
            required=False,
            label=ugettext_lazy('Notice on the ballot paper')))

    return ConfigPage(title=ugettext_lazy('Topicvoting'),
                      url='openslides_topicvoting',
                      required_permission='openslides_topicvoting.can_manage',
                      weight=130,
                      variables=(posts, ballotpaper_title, ballotpaper_text))


@receiver(post_database_setup, dispatch_uid='openslides_topicvoting_add_permissions_to_builtin_groups')
def add_permissions_to_builtin_groups(sender, **kwargs):
    """
    Adds the permissions openslides_topicvoting.can_see to the group Registered
    and openslides_topicvoting.can_manage to the group Staff.
    """
    content_type = ContentType.objects.get(app_label='openslides_topicvoting', model='topic')

    try:
        registered = get_registered_group()
    except Group.DoesNotExist:
        pass
    else:
        perm_can_see = Permission.objects.get(content_type=content_type, codename='can_see')
        registered.permissions.add(perm_can_see)

    try:
        staff = Group.objects.get(pk=4)
    except Group.DoesNotExist:
        pass
    else:
        perm_can_manage = Permission.objects.get(content_type=content_type, codename='can_manage')
        staff.permissions.add(perm_can_manage)
