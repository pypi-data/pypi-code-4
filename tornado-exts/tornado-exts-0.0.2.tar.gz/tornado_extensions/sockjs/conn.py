import sockjs.tornado
import simplejson as json

import logging
log = logging.getLogger()
logging.getLogger().setLevel(logging.DEBUG)


class BaseSockJSConnection(sockjs.tornado.SockJSConnection):
    r"""
    Base socket class that shape logic and protocol how each socket connection
    will be served by sockjs server.
    """
    _middlewares = None

    def on_message(self, message):
        r"""
        Facade method that is responsible for handling new message. Each method
        in Comet is json-like that consists of two parts.

        Notes
        -----
        Method is responsible for handling `name` part of `message` to find
        responsible event handler and call it with `args` part of `message`

        Parameters
        ----------
        message : json-like
            New incoming message to comet server.

        Examples
        --------

        >>>
        {
          'name': 'addChatMessage'
          'args': *({'message': 'hi', 'token': '21312', 'to': 10000008})
        }

        """

        data = json.loads(message)
        event, args = data["name"], data["args"]
        log.debug("ARGS {}".format(args))
        assert event not in('open', 'close', 'message'), \
            "Already reserved events!"
        assert isinstance(args, list), 'args param must be a list'

        f = getattr(self, 'on_{}'.format(event), None)
        if f and callable(f):
            if len(args) == 1 and isinstance(args[0], dict):
                f(**args[0])
            else:
                f(*args)
        else:
            log.error('event handler')
        pass