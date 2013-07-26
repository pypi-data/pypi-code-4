import sys
import threading

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
import requests


class TxtLocalException(Exception): pass


def send_sms(text, recipient_list, sender=None,
             username=None, password=None, **kwargs):
    """
    Render and send an SMS template.

    The current site will be added to any context dict passed.

        recipient_list: A list of number strings. Each number must be purely
                        numeric, so no '+' symbols, hyphens or spaces. The
                        numbers must be prefixed with their international
                        dialling codes.
                        eg. UK numbers would look like 447123456789.
        text: The message text. (Gets URI encoded.)
        sender: Must be word up to 11 characters or a number up to 14 digits.
                Defaults to settings.TXTLOCAL_FROM. (Must be a string.)
        username: Defaults to settings.TXTLOCAL_USERNAME.
        password: Defaults to settings.TXTLOCAL_PASSWORD.
        **kwargs: Will be passed through to textlocal in the POST data.

    Any unrecognised kwargs will be passed to txtlocal in the POST data.
    """
    def get_setting(setting):
        try:
            return getattr(settings, setting)
        except AttributeError:
            msg = 'The {0} settings must not be empty.'
            raise ImproperlyConfigured(msg.format(settings))

    if not sender:
        sender = get_setting('TXTLOCAL_FROM')

    if not password:
        password = get_setting('TXTLOCAL_PASSWORD')

    if not username:
        username = get_setting('TXTLOCAL_USERNAME')

    if getattr(settings, 'TXTLOCAL_DEBUG', False):
        # render to console
        with threading.RLock():
            sys.stdout.write('To:   {0}\n'.format(', '.join(recipient_list)))
            sys.stdout.write('From: {0}\n'.format(sender))
            sys.stdout.write(text)
            sys.stdout.write('\n')
            sys.stdout.write('-' * 79)
            sys.stdout.write('\n')
            sys.stdout.flush()
        return

    payload = {
        'selectednums': ','.join(recipient_list),
        'message': text,
        'uname': username or settings.TXTLOCAL_USERNAME,
        'pword': password or settings.TXTLOCAL_PASSWORD,
        'from': sender,
        'json': 1,  # This makes textlocal send us back info about the request.
    }

    url = getattr(settings, 'TXTLOCAL_ENDPOINT', 'https://www.txtlocal.com/sendsmspost.php')
    r = requests.post(url, data=payload)
    r.raise_for_status()

    available = r.json().get('CreditsAvailable')
    required = r.json().get('CreditsRequired')
    remaining = r.json().get('CreditsRemaining')
    if (
        available is None or
        required is None or
        remaining is None or
        required <= 0 or
        available - required != remaining
    ):
        err = 'Message may not have been sent. Response was: "{0}"'.format(r.json()['Error'])
        raise TxtLocalException(err)


def render_to_send_sms(template, context=None, **kwargs):
    """
    Render and send an SMS template.

    The current site will be added to any context dict passed.

    Any unrecognised kwargs will be passed to send_sms.
    """
    if context is None:
        context = {}
    context['site'] = Site.objects.get_current()
    text = render_to_string(template, context)

    send_sms(text, **kwargs)
