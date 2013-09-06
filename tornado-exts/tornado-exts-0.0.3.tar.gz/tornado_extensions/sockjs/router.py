import sockjs.tornado
from .mixins import BroadcastMixin


class CustomSockJSRouter(sockjs.tornado.SockJSRouter, BroadcastMixin):
    r"""Router is a Comet server that serves client sockets.

    Extended summary
    ----------------
    This router extends the base class `sockjs.tornado.SockJSRouter` and
    includes `BroadcastMixin`.
    """
    pass
