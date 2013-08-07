from socketio.namespace import BaseNamespace
from django.contrib.auth.models import User


class SocketList:
    all = {}
    user = {}

sockets = SocketList()

def message_user(key, message):
    """ sends a generic message to the user """
    if key is User:
        key = key.id

    if key in sockets.user:
        sockets.all.get(key).send_packet(dict(
            type="event",
            name="message",
            args=message,
            endpoint="/socketio"))


class UserNamespace(BaseNamespace):
    def on_identify(self):
        sockets.all[self.request.session.session_key] = self.socket
        if self.request.user.is_authenticated:
            sockets.user[self.request.user.id] = self.socket

        message = "Hello, %s" % str(self.request.user)

        self.emit("welcome", message)

    def recv_disconnect(self):
        try:
            del sockets[self.request.session.session_key]
        except:
            pass
