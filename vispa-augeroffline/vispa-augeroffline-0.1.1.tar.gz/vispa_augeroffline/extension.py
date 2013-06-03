# -*- coding: utf-8 -*-

# imports
from vispa import AbstractExtension

# import the controller
from controller import AugerOfflineController

class AugerOfflineExtension(AbstractExtension):

    def get_name(self):
        return 'augeroffline'

    def dependencies(self):
        return []

    def setup(self,  extensionList):
        self.controller(AugerOfflineController())
        self.js('js/augeroffline.js')
        self.css('css/styles.css')
        self.remote()