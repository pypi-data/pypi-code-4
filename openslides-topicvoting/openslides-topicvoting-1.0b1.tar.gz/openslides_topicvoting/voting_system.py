#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class and function for the voting system.
"""

from operator import attrgetter

from openslides.config.api import config

from .models import Category


class Hoechstzahl(object):
    """
    An object represents one hoechstzahl in the Sainte-Laguë method.
    """
    all_hoechstzahls = []

    def __init__(self, category, rank):
        try:
            self.topic = category.topic_set.order_by('-votes', '-weight')[rank]
        except IndexError:
            return
        else:
            self.__class__.all_hoechstzahls.append(self)
        divisor = rank * 2 + 1
        self.value = float(category.sum_of_votes) / divisor

    @classmethod
    def get_results(cls):
        """
        Generator to get all hoechstzahl objects in the winning order.
        """
        cls.all_hoechstzahls.sort(key=attrgetter('value', 'topic.category.weight'), reverse=True)
        for hoechstzahl in cls.all_hoechstzahls:
            yield hoechstzahl

    @classmethod
    def get_result_table_and_info(cls):
        """
        Returns a dictionary with a nested list (table) with all hoechstzahls
        ordered by value. This table has only as many columns as there are posts.
        Returns also some info flags for the results view and slide.
        """
        runoff_poll_warning = False

        # Point winners
        results_generator = cls.get_results()
        winning_hoechstzahls = []
        topic_post_warning = False
        for i in range(config['openslides_topicvoting_posts']):
            try:
                winning_hoechstzahls.append(results_generator.next())
            except StopIteration:
                topic_post_warning = True
                break
        else:
            try:
                first_looser_hoechstzahl = results_generator.next()
            except StopIteration:
                pass
            else:
                # First runoff poll check: Check equal hoechstzahls between the categories.
                if (first_looser_hoechstzahl.value == winning_hoechstzahls[-1].value and
                        first_looser_hoechstzahl.topic.category.weight == winning_hoechstzahls[-1].topic.category.weight):
                    runoff_poll_warning = True

        # Create table
        result_table = []
        all_categories = sorted(Category.objects.all(), key=attrgetter('sum_of_votes', 'weight'), reverse=True)
        for category in all_categories:
            category_list = []
            category_hoechstzahls = filter(lambda hoechstzahl: hoechstzahl.topic.category == category, cls.all_hoechstzahls)
            category_hoechstzahls.sort(key=lambda hoechstzahl: hoechstzahl.value, reverse=True)
            # TODO: Use a map here?
            for hoechstzahl in category_hoechstzahls:
                winner = hoechstzahl in winning_hoechstzahls
                # Second runoff poll check: Check equal votes inside a category.
                if (category_list and
                        not winner and
                        hoechstzahl.topic.votes == category_list[-1]['hoechstzahl'].topic.votes and
                        hoechstzahl.topic.weight == category_list[-1]['hoechstzahl'].topic.weight):
                    runoff_poll_warning = True
                category_list.append({'hoechstzahl': hoechstzahl, 'winner': winner})
            category_list += (config['openslides_topicvoting_posts'] - len(category_list)) * [{'hoechstzahl': None, 'winner': False}]
            result_table.append(category_list)

        # Return table and flags as dictionary
        return {'result_table': result_table, 'runoff_poll_warning': runoff_poll_warning, 'topic_post_warning': topic_post_warning}


def feed_hoechstzahls():
    """
    Initialize all hoechstzahls by parsing the first topics of all categories.
    The number of posts indicates how many topics are parsed.
    """
    # Clear existing hoechstzahls
    Hoechstzahl.all_hoechstzahls = []
    # Feed them
    for category in Category.objects.all():
        for rank in range(config['openslides_topicvoting_posts']):
            Hoechstzahl(category=category, rank=rank)
