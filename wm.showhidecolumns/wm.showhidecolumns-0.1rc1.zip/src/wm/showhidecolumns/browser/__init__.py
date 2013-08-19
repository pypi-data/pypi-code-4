from plone.app.layout.viewlets.common import ViewletBase

class ColumnsViewlet(ViewletBase):
    
    def update(self):
        disableLeft=self.context.getField('leftPortletslot').get(self.context)
        disableRight=self.context.getField('rightPortletslot').get(self.context)
        
        try:
            disableLeft = int(disableLeft)
        except ValueError:
            disableLeft = None

        try:
            disableRight = int(disableRight)
        except ValueError:
            disableRight = None
                        
        self.request.set('disable_plone.leftcolumn', disableLeft)
        self.request.set('disable_plone.rightcolumn',disableRight)
        
    def index(self):
        return u''