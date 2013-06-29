import ajenti
from ajenti.api import *
from ajenti.api.http import HttpPlugin, url
from ajenti.plugins.main.api import SectionPlugin
from ajenti.plugins.services.api import ServiceMultiplexor
from ajenti.ui import on, p, UIElement
from ajenti.ui.binder import Binder
from ajenti.plugins import manager


@plugin
class ElementsProjects (SectionPlugin):
    def init(self):
        self.title = 'Video'
        self.icon = 'suitcase'
        self.category = 'Elements'
        self.append(self.ui.inflate('elements:video-main'))
        self.opendialog = self.find('opendialog')

    def on_page_load(self):
        pass

    @on('player', 'cut')
    def on_cut(self, time=None, time_text=None):
        self.find('cut').text = 'Last cut: %.3f s (%s)' % (time, time_text)

    @on('open', 'click')
    def on_open(self):
        self.opendialog.visible = True

    @on('opendialog', 'select')
    def on_open_dialog_select(self, path=None):
        self.opendialog.visible = False
        if path:
            self.find('player').path = path
            self.find('player').position = 0
            self.find('player').autoplay = True


@p('path', type=unicode)
@p('position', type=float)
@p('autoplay', type=bool)
@plugin
class VideoElement (UIElement):
    typeid = 'video'


@plugin
class ElementsVideoServer (HttpPlugin):
    def init(self):
        pass

    @url('/elements/video/(?P<path>.+)')
    def get_page(self, context, path):
        if context.session.identity is None:
            return context.respond_forbidden()

        return context.file(path, stream=True)
