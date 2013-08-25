#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views for categories and topics.
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from openslides.config.api import config
from openslides.projector.projector import Widget, SLIDE
from openslides.utils.views import ListView, CreateView, UpdateView, DeleteView
from openslides.utils.template import Tab

from .models import Category, Topic
from .voting_system import Hoechstzahl, feed_hoechstzahls


class TopicvotingCategoryListView(ListView):
    """
    View to list all categories and all topics.
    """
    model = Category
    permission_required = 'openslides_topicvoting.can_see'

    def get_context_data(self, **kwargs):
        context = super(TopicvotingCategoryListView, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        context['lost_topics'] = Topic.objects.filter(category=None).exists()
        return context


class TopicvotingCategoryCreateView(CreateView):
    model = Category
    success_url_name = 'topicvoting_category_list'
    apply_url_name = 'topicvoting_category_list'  # TODO: Remove this when openslides/utils/views.py changed from 'edit' to 'update'.
    permission_required = 'openslides_topicvoting.can_manage'


class TopicvotingCategoryUpdateView(UpdateView):
    model = Category
    success_url_name = 'topicvoting_category_list'
    apply_url_name = 'topicvoting_category_list'  # TODO: Remove this when openslides/utils/views.py changed from 'edit' to 'update'.
    permission_required = 'openslides_topicvoting.can_manage'


class TopicvotingCategoryDeleteView(DeleteView):
    model = Category
    success_url_name = 'topicvoting_category_list'
    permission_required = 'openslides_topicvoting.can_manage'


class TopicvotingTopicCreateView(CreateView):
    model = Topic
    success_url_name = 'topicvoting_category_list'
    apply_url_name = 'topicvoting_category_list'  # TODO: Remove this when openslides/utils/views.py changed from 'edit' to 'update'.
    permission_required = 'openslides_topicvoting.can_manage'


class TopicvotingTopicUpdateView(UpdateView):
    model = Topic
    success_url_name = 'topicvoting_category_list'
    apply_url_name = 'topicvoting_category_list'  # TODO: Remove this when openslides/utils/views.py changed from 'edit' to 'update'.
    permission_required = 'openslides_topicvoting.can_manage'


class TopicvotingTopicDeleteView(DeleteView):
    model = Topic
    success_url_name = 'topicvoting_category_list'
    permission_required = 'openslides_topicvoting.can_manage'


class TopicvotingResultView(TopicvotingCategoryListView):
    """
    View to show the results in a nice table.
    """
    template_name = 'openslides_topicvoting/result.html'
    permission_required = 'openslides_topicvoting.can_see'

    def get_context_data(self, **kwargs):
        """
        Inserts the results table and additional flags and variables into the context.
        """
        context = super(TopicvotingResultView, self).get_context_data(**kwargs)
        feed_hoechstzahls()
        result_table_and_info = Hoechstzahl.get_result_table_and_info()
        context['result_table'] = result_table_and_info['result_table']
        context['runoff_poll_warning'] = result_table_and_info['runoff_poll_warning']
        context['topic_post_warning'] = result_table_and_info['topic_post_warning']
        context['divisors'] = map(lambda rank: rank * 2 + 1, range(config['openslides_topicvoting_posts']))
        return context


def register_tab(request):
    """
    Registers the main menu entry (tab).
    """
    from . import BASE_URL
    return Tab(
        title=_('Topicvoting'),
        app='openslides_topicvoting',
        stylefile='styles/openslides_topicvoting.css',
        url=reverse('topicvoting_category_list'),
        permission=request.user.has_perm('openslides_topicvoting.can_see'),
        selected=request.path.startswith('/%s/' % BASE_URL))


def get_widgets(request):
    """
    Returns the widget.
    """
    return [Widget(
        request,
        name='topicvoting',
        display_name=_('Topicvoting'),
        template='openslides_topicvoting/category_widget.html',
        context={'overview_slide': SLIDE['topicvotingoverview'],
                 'result_slide': SLIDE['topicvotingresult'],
                 'category_list': Category.objects.all()},
        permission_required='projector.can_manage_projector',
        default_column=1)]
