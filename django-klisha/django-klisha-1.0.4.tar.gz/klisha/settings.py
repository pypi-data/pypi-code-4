# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from django.conf import settings

KLISHA_WEBSITE_NAME = getattr(settings, 'KLISHA_WEBSITE_NAME', "klisha - an example site")
KLISHA_WEBSITE_DESCRIPTION = getattr(settings, 'KLISHA_WEBSITE_DESCRIPTION', "description")
KLISHA_GOOGLE_ANALYTICS_KEY  = getattr(settings, 'KLISHA_GOOGLE_ANALYTICS_KEY', "")
KLISHA_PAGINATE_BY = getattr(settings, 'KLISHA_PAGINATE_BY', 12)
KLISHA_RELATED_PICTURE_NUMBER = getattr(settings, 'KLISHA_PAGINATE_BY', 3)