from tomcom.browser.public import *

class ITCContentReferenceBrowser(Interface):

    def get(self):
        """ """

class Browser(BrowserView):

    implements(ITCContentReferenceBrowser)

    def get(self):

        context=self.context
        pc=context.getAdapter('pc')()


        query={}
        query['portal_type']='TCBlog'
        query['sort_on']='created'
        query['sort_order']='reverse'
        query['path']={'query':context.getPath(),
                       'depth':1}

        return pc(query)