# -*- coding: utf-8 -*-
import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPBadRequest

log = logging.getLogger(__name__)


@view_config(route_name='clientlogs')
def log_view(request):
    message = unicode(request.body, request.charset, errors='replace')
    logger_name = request.matchdict['logger_name']
    log_level = request.matchdict['log_level']
    # checking for valid log level is already done by the route
    send_log(logger_name, log_level, message)
    return HTTPOk()


@view_config(route_name='clientlogs_batch')
def batch_log_view(request):
    try:
        logs = request.json['logs']
    except (ValueError, KeyError):
        raise HTTPBadRequest('Missing logs parameter')
    for elem in logs:
        try:
            logger_name, log_level, message = extract_attributes(elem)
        except KeyError:
            return HTTPBadRequest('Missing statement property')
        try:
            send_log(logger_name, log_level, message)
        except AttributeError:
            return HTTPBadRequest('Invalid log level')
    return HTTPOk()


def send_log(logger_name, log_level, message):
    logger = logging.getLogger(logger_name)
    getattr(logger, log_level)(message)


def extract_attributes(elem):
    logger_name = elem['logger_name']
    message = elem['body']
    log_level = elem['log_level']
    return logger_name, log_level, message
