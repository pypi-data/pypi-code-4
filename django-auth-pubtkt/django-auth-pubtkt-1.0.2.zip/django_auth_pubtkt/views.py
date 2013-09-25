# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Alexander Vyushkov
# All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from django.shortcuts import redirect
from django.conf import settings
import urllib

def redirect_to_sso(request):
    back = request.is_secure() and 'https://' or 'http://'
    back = back + request.get_host() + request.GET["next"]
    back = urllib.quote_plus(back)
    try:
        TKT_AUTH_BACK_ARG_NAME = settings.TKT_AUTH_BACK_ARG_NAME
    except AttributeError:
        TKT_AUTH_BACK_ARG_NAME = "back"

    url = settings.TKT_AUTH_LOGIN_URL + "?" + TKT_AUTH_BACK_ARG_NAME + "=" + back
    return redirect(url)