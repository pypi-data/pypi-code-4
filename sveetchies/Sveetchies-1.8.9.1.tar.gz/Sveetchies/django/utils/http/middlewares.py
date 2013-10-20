# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.conf import settings
from django.core.exceptions import PermissionDenied

from Sveetchies.django.utils.http import Http403
from Sveetchies.django.utils.http.shortcuts import render_to_403

class Http403Middleware(object):
    def process_exception(self,request,exception):
        if isinstance(exception, Http403):
            if settings.DEBUG:
                raise PermissionDenied
            return render_to_403(context_instance=RequestContext(request))
