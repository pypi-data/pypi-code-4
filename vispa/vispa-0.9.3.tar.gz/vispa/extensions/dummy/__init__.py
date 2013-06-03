# -*- coding: utf-8 -*-

# imports
import vispa.rpc
from vispa import AbstractExtension

# we import the controller from a seperate file
from controller import DummyController

class DummyExtension(AbstractExtension):

    def get_name(self):
        return 'dummy'

    def dependencies(self):
        return []

    def setup(self, extensions):
        self.controller(DummyController())
        self.js('js/extension.js')
        self.css('css/styles.css')
        self.remote()
