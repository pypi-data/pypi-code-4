#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect


NAME = 'openslides-topicvoting'
VERSION = '1.0b1'
DESCRIPTION = 'Topic Voting Plugin for OpenSlides'
BASE_URL = 'openslides_topicvoting'  # TODO: Rename to topicvoting when the functionality is implemented in OpenSlides


if not inspect.stack()[1][4][0] == ('from openslides_topicvoting import NAME, VERSION, DESCRIPTION  '
                                    '# Ohf9du1Kae8aiVayu3ahSaiZei0PhugiSu1eiMai\n'):
    # Don't import signals, slides and urlpatters if the import of this module
    # came from the setup.py for then the settings are not present.
    from . import signals
    from . import slides
    from .urls import urlpatterns
    URLPATTERS = urlpatterns


def get_name():
    """
    Function for OpenSlides' version page.
    """
    return '%s (%s)' % (DESCRIPTION, NAME)
