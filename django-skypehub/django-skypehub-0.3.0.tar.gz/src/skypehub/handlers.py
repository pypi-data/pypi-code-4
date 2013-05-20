from collections import defaultdict
from select import select
from time import time
from struct import pack, unpack

from Skype4Py.errors import SkypeAPIError

from skypehub.models import Message
from skypehub.utils import is_windows, get_skype


def message_logging_receiver(handler, message, status):
    Message.objects.create(
        body=message.Body,
        sender=message.Sender.Handle,
        chat_name=message.Chat.Name,
    )


class OnMessageHandler(object):
    """
    Skype OnMessage event handler
    """
    default_statuses = ('RECEIVED',)
    default_receivers = ()

    def __init__(self, skype=None):
        self.receivers = defaultdict(lambda: set())
        for status in self.default_statuses:
            for receiver in self.default_receivers:
                self.receivers[status].add(receiver)
        self.skype = skype

    def connect(self, receiver, statuses=None):
        if statuses is None:
            statuses = list(self.default_statuses)
        for status in statuses:
            self.receivers[status].add(receiver)

    def dispatch(self, message, status):
        try:
            for receiver in self.receivers[status]:
                receiver(self, message, status)
        except SkypeAPIError, err:
            # reconnect skype
            get_skype(force_create=True)


class OnTimeHandler(object):
    """
    Skype OnTime event handler
    by moriyoshi
    """
    def __init__(self, skype=None):
        self.skype = skype
        # TODO: socketpair does not work on Windows.
        from socket import socketpair
        self.pair = socketpair()
        self.timepoints = []
        self.callables = {}
        self._callables = {}
        self.id = 1

    def connect(self, callable, time):
        id = self.callables.get(callable, 0)
        if not id:
            id = self.id
            self.id += 1
            self.callables[callable] = id
            self._callables[id] = callable
        self.pair[1].send(pack("@ii", time, id))

    def __call__(self):
        wait = None
        while True:
            r, w, e = select([self.pair[0]], [], [], wait)
            if r:
                t, id = unpack("@ii", r[0].recv(8))
                i = self.search_nearest(t)
                self.timepoints.insert(i, (t, id))
                wait = max(self.timepoints[0][0] - time(), 0)
            else:
                _time, id = self.timepoints.pop(0)
                self._callables[id](self, _time)
                if self.timepoints:
                    wait = max(self.timepoints[0][0] - time(), 0)
                else:
                    wait = None

    def search_nearest(self, time):
        l = len(self.timepoints)
        if l == 0:
            return 0
        s = 0
        e = l

        while True:
            i = (s + e) // 2
            if self.timepoints[i][0] < time:
                s = i
                i = (i + e) // 2
                if i == l - 1:
                    i = l
                    break
            else:
                e = i
                i = (s + i) // 2
                if i == 0:
                    break
        return i


on_message = OnMessageHandler()
if is_windows():
    def on_time():
        import time
        while True:
            time.sleep(1)
else:
    on_time = OnTimeHandler()
on_message.connect(message_logging_receiver)
