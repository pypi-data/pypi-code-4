#coding:utf-8
class Dispatcher(object):
    def dispatch(self, key):
        """
        """
        raise NotImplementedError()

    def start_consumer(self):
        """
        Start a new message consumer. We'll call message_consumer with every new message.
        """
        raise NotImplementedError()

    @property
    def messages(self):
        raise NotImplementedError()

