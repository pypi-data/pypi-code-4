#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slides for an overview of all categories and for the results.
"""

from django.utils.translation import ugettext as _, ugettext_lazy, pgettext, pgettext_lazy

from openslides.config.api import config
from openslides.projector.api import register_slidemodel, register_slidefunc

from .models import Category
from .voting_system import Hoechstzahl, feed_hoechstzahls


def overview_slide():
    """
    Slide with all categories. Similar to ListView. Lost topics are not shown.
    """
    return {
        'title': pgettext('topicvoting', 'All categories'),
        'template': 'openslides_topicvoting/overview_slide.html',
        'category_list': Category.objects.all()}


def result_slide():
    """
    Slide for a table with all results. The winning topics are given too.
    """
    feed_hoechstzahls()
    result_table_and_info = Hoechstzahl.get_result_table_and_info()
    return {'title': _('Results'),
            'template': 'openslides_topicvoting/result_slide.html',
            'result_table': result_table_and_info['result_table'],
            'runoff_poll_warning': result_table_and_info['runoff_poll_warning'],
            'topic_post_warning': result_table_and_info['topic_post_warning'],
            'divisors': map(lambda rank: rank * 2 + 1, range(config['openslides_topicvoting_posts']))}


register_slidemodel(Category)
register_slidefunc('topicvotingoverview', overview_slide, name=pgettext_lazy('topicvoting', 'All categories'))
register_slidefunc('topicvotingresult', result_slide, name=ugettext_lazy('Results'))
