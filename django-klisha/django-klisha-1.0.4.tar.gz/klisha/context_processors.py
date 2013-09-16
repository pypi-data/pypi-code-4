# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from klisha import settings as sett

def settings(request):
    return {
        'WEBSITE_NAME': sett.KLISHA_WEBSITE_NAME,
        'WEBSITE_DESCRIPTION': sett.KLISHA_WEBSITE_DESCRIPTION,
        'GOOGLE_ANALYTICS_KEY': sett.KLISHA_GOOGLE_ANALYTICS_KEY,
    }


