# Copyright (c) 2013 Andriy Gushuley
# Licensed under the terms of the MIT License (see LICENSE.txt)
from django.conf import settings

MULTIHOST_DEFAULT_URLS = [
  'gushuley.multisite.urls',
]


def get_available_urls():
    return [(i, i) for i in getattr(settings, "MULTIHOST_AVAILABLE_URLS", MULTIHOST_DEFAULT_URLS)]


def is_database_driven_modules_urls():
    return getattr(settings, "MULTIHOST_DATABASE_DRIVEN_URLS", False)