import logging

from pytool.cmd import Command

from pyimpact import server


class Main(Command):
    def set_opts(self):
        self.opt('--port', '-p', default=8080, type=int, help="select the port")
        self.opt('--host', '-h', default='localhost', help="select the host")

    def run(self):
        server.run_server(port=self.args.port, host=self.args.host)
