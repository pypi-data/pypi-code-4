#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)


''' Stub module for FondaSMS requests processing.

    Following functions are named after the event that triggers them.
    Implement them in your own module and give the module name
    in the configuration.

    Every function takes a single argument named payload.
    If is the request.POST from the HTTP request: a dict containing
    all the parameters from the Android app.

    Additionnaly, there is an auto-reply feature.
    If enabled, it will automatically trigger a response on each
    *incoming* request (sms, call, mms).

    All handlers (`handle_*`) does not need to return anything.

    The content of that response if either the content
    of the `automatic_reply_text` variable or taken from
    the return of `automatic_reply_handler()`.

    Variable `automatic_reply_via_handler` decides which way to follow.

    Configuration is done in the `urlpattern` definition.
    Bellow is an example settings all the available variables:

    url(r'^fondasms/?$', 'fondasms.views.fondasms_handler',
        {'handler_module': 'douentza.fondahandlers',
         'send_automatic_reply': False,
         'automatic_reply_via_handler': False,
         'automatic_reply_text': ("Merci. On a bien enregistré votre demande. "
                                  "On vous rappelle bientôt.")},
        name='fondasms') '''


def handle_incoming_call(payload):
    ''' Handles an `incoming` action with `type` being `call` '''
    return


def handle_incoming_sms(payload):
    ''' Handles an `incoming` action with `type` being `sms` '''
    return


def handle_outgoing_status_change(payload):
    ''' Handles changes in ougoing message status. Used for DLR. '''
    return


def handle_device_status_change(payload):
    ''' Handles changes in device status such as battery or network '''
    return


def reply_with_phone_number(payload):
    ''' Called to specify a destination phone number (not end user's one)

        which should handle the request.
        Used by isafonda gateway to route outgoing messages in environment
        with multiple phones.

        Return None or a string being the phone_number. '''
    return None

def automatic_reply_handler(payload):
    ''' Called when auto-reply is ON and via-handler is ON too.

        Must return a list of messages dict {to: xx, message: yy} '''
    return
