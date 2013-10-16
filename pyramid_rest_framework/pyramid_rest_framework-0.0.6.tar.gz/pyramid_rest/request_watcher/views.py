#-*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid_rest.events import EventManager
from pyramid_rest.exceptions import UnknownError
from pyramid_rest.request import Request
from pyramid_rest.logger import Logger
import traceback
from pyramid_rest.response import Response

def process_pyramid_500_view(error, request):
    Logger().main.error("Getted 500 error, info: \n%s", traceback.format_exc())
    request = Request(request)
    error = UnknownError(info = "Api error")
    responseClass = Response(request, error.serialize(request), error.code)
    request.request.response.status_code = 500
    EventManager().trigger("before-response", None, request, responseClass)
    return responseClass.serialize()