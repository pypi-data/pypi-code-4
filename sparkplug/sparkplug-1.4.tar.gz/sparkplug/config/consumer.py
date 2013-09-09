"""Consumer configuration
=========================

.. highlight:: ini

To add consumers to a sparkplug instance, include one or more ``[consumer:*]``
sections in your configuration::

    [consumer:echo]
    # Entry point identifier
    use = sparkplug#echo
    # Queue to consume against
    queue = events
    # Other parameters will be passed passed to the entry point
    format = %%(body)s

The ``use`` parameter is used to find a ``pkg_resources`` entry point. For the
example above, an entry point named ``echo`` in the ``sparkplug.consumers``
group for a distribution (usually, an ``egg`` file) named ``sparkplug`` will
be loaded and used to create message consumers.

---------------------
The consumer protocol
---------------------

.. highlight:: python

Once sparkplug finds an entry point, it uses something equivalent to::

    callback = entry_point(channel, **config)
    channel.basic_consume(queue=queue, callback=callback)

to configure each channel. When sparkplug shuts down, the callback is
also unregistered cleanly.

To register entry points in your own egg files, use ``setuptools``'
``entry_points`` mechanism::

    setup(
        # ...
        entry_points = {
            # ...
            'sparkplug.consumers': [
                'echo = sparkplug.examples:EchoConsumer'
            ]
        }
    )

A complete example is included in the sparkplug source.
"""

import pkg_resources
from sparkplug.config import DependencyConfigurer
from sparkplug.logutils import LazyLogger

_log = LazyLogger(__name__)

def parse_use(group, use, load_entry_point=pkg_resources.load_entry_point):
    """Parses and loads the entry point for a 'use' directive. The ``use``
    string is expected to look like ``dist#name`` and will be split on the
    first ``'#'`` into a ``dist, name`` pair. Then we pass the whole lot
    to the ``load_entry_point`` callback (using the same protocol as 
    ``pkg_resources.load_entry_point``) and return whatever we get back.
    
    :param group: the entry point group to load from.
    :param use: the un-parsed ``use`` string.
    :param load_entry_point: the function that will actually load entry points.
    """
    dist, entry_point = use.split('#', 1)
    return load_entry_point(dist, group, entry_point)

class ConsumerConfigurer(DependencyConfigurer):
    """Handles per-channel setup and teardown for consumer blocks in the
    sparkplug config file.
    
    :param name: the name of the consumer section.
    :param configurer: the configuration builder to configure with 
        callbacks.
    :param use: the consumer entry point to look up.
    :param queue: the queue to bind to.
    :param **kwargs: other configuration parameters, which will be
        passed along to the ``use`` callback.
    """
    def __init__(self, name, use, queue, **kwargs):
        DependencyConfigurer.__init__(self)
        self.entry_point = self.parse_use('sparkplug.consumers', use)
        self.queue = queue
        self.consumer_params = kwargs
        
        self.depends_on(queue)
    
    def start(self, channel):
        _log.debug("Creating consumer from %r", self.entry_point)
        consumer = self.entry_point(channel, **self.consumer_params)
        
        _log.debug("Consuming from queue %s", self.queue)
        channel.basic_consume(callback=consumer, queue=self.queue)

    def stop(self, channel):
        pass
    
    parse_use = staticmethod(parse_use)