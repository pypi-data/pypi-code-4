#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from fondasms.utils import import_path, outgoing_for


def fondasms_tester(request):
    ''' display the HTML tester to generate fake events '''
    return render(request, 'fonda_tester.html', {})


@csrf_exempt
def fondasms_handler(request, **options):
    ''' Received FondaSMS HTTP requests and process them

        Processing based on module and other options passed
        as kwargs to the view.

        see example in urls.py '''

    stub = 'fondasms.stub'
    mod = options.get('handler_module')
    if options.get('handler_module') is None:
        mod = stub

    # import handlers
    handle_incoming_call = import_path('handle_incoming_call', module=mod, fallback=stub)
    handle_incoming_sms = import_path('handle_incoming_sms', module=mod, fallback=stub)
    handle_outgoing_status_change = import_path('handle_outgoing_status_change', module=mod, fallback=stub)
    handle_device_status_change = import_path('handle_device_status_change', module=mod, fallback=stub)
    reply_with_phone_number = import_path('reply_with_phone_number', module=mod, fallback=stub)
    automatic_reply_handler = import_path('automatic_reply_handler', module=mod, fallback=stub)

    action = request.POST.get("action")
    handler = lambda x: None
    outgoings = []

    if action == "incoming":
        if request.POST.get('message_type') == 'call':
            handler = handle_incoming_call
        if request.POST.get('message_type') == 'sms':
            handler = handle_incoming_sms
        outgoings += handle_automatic_reply(payload=request.POST,
                                            options=options,
                                            handler=automatic_reply_handler) or []
    elif action == "outgoing":
        pass
    elif action == 'send_status':
        handler = handle_outgoing_status_change
    elif action == 'device_status':
        handler = handle_device_status_change
    else:
        return HttpResponse(json.dumps({}), mimetype='application/json')

    try:
        outgoings += handler(request.POST) or []
        if not isinstance(outgoings, list):
            outgoings = []
    except Exception as e:
        response = {'error': {'message': str(e)}}
        return HttpResponse(json.dumps(response),
                            mimetype='application/json',
                            status=500)

    response = {"events": [],
                "phone_number": reply_with_phone_number(request.POST)}
    if len(outgoings):
        response['events'].append({"event": "send",
                            "messages": outgoings})

    return HttpResponse(json.dumps(response),
                        mimetype='application/json')


def handle_automatic_reply(payload, options, handler=None):

    if not options.get('send_automatic_reply', False):
        return []

    message = None
    if options.get('automatic_reply_via_handler', False):
        message = handler(payload)
    elif len(options.get('automatic_reply_text', '')):
        message = options.get('automatic_reply_text', '-')

    if message:
        return [outgoing_for(to=payload.get('from'),
                             message=message)]

    return []
