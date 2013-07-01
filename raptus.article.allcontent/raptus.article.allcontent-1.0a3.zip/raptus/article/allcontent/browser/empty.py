from plone.app.layout.viewlets.common import ViewletBase


class EmptyViewlet(ViewletBase):

    def update(self):
        return

    def render(self):
        return u''
