from reconfigure.items.ajenti import UserData
from ajenti.plugins.main.api import SectionPlugin
from ajenti.api import plugin
from ajenti.ui import on
from ajenti.ui.binder import Binder
import ajenti
from ..projects.main import ElementsProjectManager


@plugin
class ElementsUsers (SectionPlugin):
    def init(self):
        self.title = 'Users'
        self.icon = 'group'
        self.category = 'Elements'
        self.append(self.ui.inflate('elements:users-main'))
        self.binder_users = Binder(ajenti.config.tree, self)

        self.mgr = ElementsProjectManager.get()

        def post_user_bind(o, c, i, u):
            u.find('name-edit').visible = i.name != 'root'
            u.find('name-label').visible = i.name == 'root'
            u.find('status').text = 'Online' if i.name in self.mgr.active_users else 'Offline'
            u.find('projects').text = ', '.join(x.name for x in self.mgr.active_users.get(i.name, []))

        self.find('users').post_item_bind = post_user_bind
        self.find('users').new_item = lambda c: UserData()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.binder_users.reset().autodiscover().populate()

    @on('save', 'click')
    def save(self):
        self.binder_users.update()
        ajenti.config.save()
        self.refresh()
