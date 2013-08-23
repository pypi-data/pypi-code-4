import os
import re

from spreads.plugin import HookPlugin


class HTMLPlugin(HookPlugin):
    def __init__(self, config):
        self.config = config['postprocess']
