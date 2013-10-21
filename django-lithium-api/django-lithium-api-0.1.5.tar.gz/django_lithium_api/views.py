# -*- coding: utf-8 -*-
import re

from lxml import etree

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from django.views.generic import FormView
from django.views.generic.base import View
from django_lithium_api.forms import LithiumAuthenticationForm
from django_lithium_api import types
from django_lithium_api import signals

class AuthenticationView(FormView):
    form_class = LithiumAuthenticationForm

class Webhook(View):

    def post(self, request):
        data = request.POST
        token = data.get('token')
        event_type = data.get('event.type')
        message = data.get('message')
        handler = self.get_handler(event_type)
        success = False
        xml = etree.fromstring(message)
        try:
            lithium_obj = types.xml_to_type(xml)
            handler(lithium_obj, token, message)
            return HttpResponse('OK')
        except Exception:
            # TODO: logging
            resp = HttpResponseServerError()
            resp.status_code = 503
            return resp
        
    def handle_message_create(self, obj, token, raw_xml):
        """
        Issued when a new message (e.g., topics, replies, blog articles, comments, etc.) is created
        """
        signals.message_create.send(self, message=obj, token=token, raw_xml=raw_xml)

    def handle_message_update(self, obj, token, raw_xml):
        """
        Issued when a message is successfully edited
        """
        signals.message_update.send(self, message=obj, token=token, raw_xml=raw_xml)

    def handle_message_move(self, obj, token, raw_xml):
        """
        Issued when a message is moved from one community section (e.g., board, blog, etc.) to another
        """
        signals.message_move.send(self, message=obj, token=token, raw_xml=raw_xml)

    def handle_message_delete(self, obj, token, raw_xml):
        """
        Issued when a message is deleted from the community
        """
        signals.message_delete.send(self, message=obj, token=token, raw_xml=raw_xml)

    def handle_user_create(self, obj, token, raw_xml):
        """
        Issued when a user is created in the community
        """
        signals.user_create.send(self, user=obj, token=token, raw_xml=raw_xml)

    def handle_user_update(self, obj, token, raw_xml):
        """
        Issued when a user updates his preferences (or has his preferences updated by a community administrator)
        """
        signals.user_update.send(self, user=obj, token=token, raw_xml=raw_xml)

    def handle_user_sign_on(self, obj, token, raw_xml):
        """
        Issued when a user signs into the community
        """
        signals.user_signon.send(self, user=obj, token=token, raw_xml=raw_xml)

    def handle_user_sign_off(self, obj, token, raw_xml):
        """
        Issued when a user signs out of the community
        """
        signals.user_signoff.send(self, user=obj, token=token, raw_xml=raw_xml)

    def get_handler(self, event_type):
        handler_name = 'handle_' + self._un_camel_case(event_type)
        return getattr(self, handler_name)

    def _un_camel_case(self, camel):
        """
        http://stackoverflow.com/q/1175208/45691
        """
        camel = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel).lower()