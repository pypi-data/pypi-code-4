# -*- coding: utf-8 -*-

# imports
from vispa import AbstractExtension

# import the controller
from controller import GuiDummyController


class GuiDummyExtension(AbstractExtension):

    def get_name(self):
        return 'guidummy'

    def dependencies(self):
        return []

    def setup(self, extensionList):
        self.controller(GuiDummyController())
        self.js('js/extension.js')
        self.css('css/styles.css')
        self.remote()