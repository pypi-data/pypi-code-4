from tomcom.adapter.public import *

class IUpdateActualUrl(Interface):
    pass

class Adapter(Base):

    def __call__(self,url):
        context=self.context
        context.REQUEST['ACTUAL_URL']=url