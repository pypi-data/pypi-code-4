# -*- coding: utf-8 -*-

# imports
import vispa.rpc
from vispa import AbstractExtension

# we import the controller from a seperate file
from controller import DemoController

class DemoExtension(AbstractExtension):

    def get_name(self):
        return 'demo'

    def dependencies(self):
        return []

    def setup(self, extensions):
        self.controller(DemoController())
        self.js('js/extension.js')
        self.css('css/styles.css')
        self.remote()
