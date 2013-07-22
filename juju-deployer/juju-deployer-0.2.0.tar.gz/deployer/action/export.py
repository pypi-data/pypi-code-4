import logging

from .base import BaseAction


class Export(BaseAction):

    log = logging.getLogger("deployer.export")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment
        self.env_status = None
        self.env_state = {'services': {}, 'relations': {}}

    def run(self):
        pass
