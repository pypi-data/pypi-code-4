#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


class PyOver(object):
    """
    Class to interface with the Pushover service.

    We do minimal error checking for now, this will change when we know more
    about the API.
    """

    def __init__(self,
                 token,
                 user_key,
                 device=False):
        """
        Intialises a pushover object.

        The following arguments are compulsary:
            - token: The application token.
            - user_key: The user key

        The following arguments are optional:
            - device: What device to send the message to.
        """
        if token and user_key:
            self.params = {'token': token, 'user': user_key}
            if device:
                self.device = device
        else:
            raise RuntimeError('Incomplete credentials.')

    def send_message(self, message, **kwargs):
        """
        Sends a pushover message.

        The following argument is compulsary:
            - message: The message to send.

        The following arguments are optional:
            - title: The message title.
            - url: A supplementary URL to send with the message.
            - url_title: A title for the URL mentioned above.
            - priority: Priority of the message.
            - timestamp: Timestamp of the message.
            - sound: Sound for the message to trigger.
        """
        # TODO: Do sanity checking on the arguments, make timestamp accept
        # datetimestamps, error out when given invalid parameters.
        optional_args = ['title', 'url', 'url_title', 'priority', 'timestamp',
                         'sound']

        message_params = {arg: kwargs[arg]
                          for arg in optional_args
                          if kwargs.get(arg, False)}
        message_params.update(self.params)
        message_params['message'] = message
        req = requests.post('https://api.pushover.net/1/messages.json',
                            data=message_params)

        req.raise_for_status()
        return req.json()
