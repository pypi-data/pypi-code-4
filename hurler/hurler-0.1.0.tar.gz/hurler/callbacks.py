from __future__ import absolute_import
from __future__ import unicode_literals
from collections import defaultdict


class Callbacks(object):
    def __init__(self):
        super(Callbacks, self).__init__()

        self.callbacks = defaultdict(list)

    def register(self, event_name):
        """
        Decorator,

        Registers the decorated function as a callback for the `event_name`
        given.

        :param event_name: The name of the event to register for.

        Example:
            >>> callbacks = Callbacks()
            >>> @callbacks.register("my_event")
            ... def hello():
            ...     print("Hello world")
            ...
            >>> # Which then can be called
            >>> callbacks.call("my_event")
            Hello world

        """
        def registrar(func):
            self.callbacks[event_name].append(func)

            return func

        return registrar

    def call(self, event_name, *args, **kwargs):
        """
        Method,

        Calls all callbacks registered for `event_name`. The arguments given
        are passed to each callback.

        :param event_name: The event name to call the callbacks for.
        :param args: The positional arguments passed to the callbacks.
        :param kwargs: The keyword arguments passed to the callbacks.

        Example:
            >>> callbacks = Callbacks()
            >>> @callbacks.register("my_event")
            ... def hello(your_name):
            ...     print("Hello %s, how are you today." % your_name)
            ...
            >>> callbacks.call("my_event", "Wessie")
            Hello Wessie, how are you today.

        """
        for callback in self.callbacks[event_name]:
            # Handle errors (and maybe return values)
            callback(*args, **kwargs)
