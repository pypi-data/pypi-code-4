# coding: utf-8
from collections import OrderedDict
from django.http import HttpResponse, Http404
from django_relinking.content_types import objects_choices

import json


def get_objects(request):
    try:
        return HttpResponse(
            json.dumps(OrderedDict(objects_choices(request.POST['content_type']))),
            content_type="text/json; charset=utf8"
        )
    except IndexError:
        raise Http404
