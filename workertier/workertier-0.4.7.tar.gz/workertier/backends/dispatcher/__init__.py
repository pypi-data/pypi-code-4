#coding:utf-8
class Dispatcher(object):
    def dispatch(self, key):
        """

        """
        raise NotImplementedError()

    def start_consumer(self, message_consumer):
        """
        Start a new message consumer. We'll call message_consumer with every new message.

        """
        raise NotImplementedError()

