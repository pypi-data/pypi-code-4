import logging
from cliff.command import Command
from inkwave.core import env


class Data(Command):
    site = True
    log = logging.getLogger(__name__)

    def take_action(self, args):
        self.app.stdout.write('aaa\n')
        env.init_db()
