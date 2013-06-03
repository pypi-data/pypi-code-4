# -*- coding: utf-8 -*-

import cherrypy

from vispa import AbstractExtension
from vispa.controller import AbstractController

class FileBrowserController(AbstractController):
    pass

class FileBrowserExtension(AbstractExtension):

    def get_name(self):
        return 'file'

    def dependencies(self):
        return []

    def setup(self, extensionList):
        self.controller(FileBrowserController())
        self.js('js/base/base.js')
        self.js('js/base/view.js')
        self.js('js/base/actions.js')
        self.js('js/base/events.js')
        self.js('js/base/items.js')
        self.js('js/base/selections.js')
        self.js('js/base/views/symbol/view.js')
        self.js('js/base/views/table/view.js')

        self.js('js/browser/browser.js')
        self.js('js/browser/view.js')
        self.js('js/browser/actions.js')

        self.js('js/selector/selector.js')
        self.js('js/selector/view.js')
        self.js('js/selector/actions.js')

        self.js('js/extension.js')

        self.css('css/base/base.css')
        self.css('css/base/views/symbol/symbol.css')
        self.css('css/base/views/table/table.css')
