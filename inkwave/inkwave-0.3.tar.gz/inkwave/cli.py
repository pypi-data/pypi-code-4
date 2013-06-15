import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from inkwave.core import env


VERSION = '0.3'
DESCRIPTION = 'InkWave'


class InkWave(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        super(InkWave, self).__init__(
            description=DESCRIPTION,
            version=VERSION,
            command_manager=CommandManager('inkwave.cli'),
        )

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)
        if getattr(cmd.__class__, 'site', False):
            cwd = os.getcwd()
            if os.path.exists(os.path.join(cwd, 'config.py')):
                sys.path.append(cwd)
                try:
                    import config
                    env.init(cwd, config)
                except ImportError:
                    raise
            else:
                raise RuntimeError("this command should be run inside"
                                   " site directory")

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = InkWave()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
