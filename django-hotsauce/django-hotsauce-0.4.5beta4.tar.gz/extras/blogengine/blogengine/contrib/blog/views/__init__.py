#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Details views"""

from urlparse import parse_qsl
from datetime import datetime
from operator import attrgetter

from django.template import RequestContext

from notmm.dbapi.orm.decorators import with_schevo_database
from notmm.utils.django_settings import LazySettings
from notmm.utils import paginator

from blogengine.config          import ObjectDoesNotExist
from blogengine.template        import direct_to_template
from blogengine.contrib.api_v1  import CategoryManager
from blogengine.contrib.comments import CommentForm

import logging
log = logging.getLogger('notmm.controllers.wsgi') # Change to 'blogengine' someday

settings = LazySettings()
DATABASE_NAME = settings.SCHEVO['DATABASE_NAME']

