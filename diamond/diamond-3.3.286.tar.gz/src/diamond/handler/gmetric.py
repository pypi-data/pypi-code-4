# coding=utf-8

"""
Emulate a gmetric client for usage with
[Ganglia Monitoring System](http://ganglia.sourceforge.net/)
"""

from Handler import Handler
import gmetric


class GmetricHandler(Handler):
    """
    Implements the abstract Handler class, sending data the same way that
    gmetric does.
    """

    def __init__(self, config=None):
        """
        Create a new instance of the GmetricHandler class
        """
        # Initialize Handler
        Handler.__init__(self, config)

        # Initialize Data
        self.socket = None

        # Initialize Options
        self.host = self.config['host']
        self.port = int(self.config['port'])
        self.protocol = self.config['protocol']
        if not self.protocol:
            self.protocol = 'udp'

        # Initialize
        self.gmetric = gmetric.Gmetric(self.host, self.port, self.protocol)

    def __del__(self):
        """
        Destroy instance of the GmetricHandler class
        """
        self._close()

    def process(self, metric):
        """
        Process a metric by sending it to a gmond instance
        """
        # Just send the data as a string
        self._send(metric)

    def _send(self, metric):
        """
        Send data to gmond.
        """
        metric_name = self.get_name_from_path(metric.path)
        tmax = "60"
        dmax = "0"
        slope = "both"
        # FIXME: Badness, shouldn't *assume* double type
        metric_type = "double"
        units = ""
        group = ""
        self.gmetric.send(metric_name,
                          metric.value,
                          metric_type,
                          units,
                          slope,
                          tmax,
                          dmax,
                          group)

    def _close(self):
        """
        Close the connection
        """
        self.gmetric = None
