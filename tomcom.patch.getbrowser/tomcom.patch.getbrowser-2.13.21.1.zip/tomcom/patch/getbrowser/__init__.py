from OFS.SimpleItem import Item

def get_browser(self,name):
    return self.restrictedTraverse(name)

Item.get_browser=get_browser
Item.getBrowser=get_browser
