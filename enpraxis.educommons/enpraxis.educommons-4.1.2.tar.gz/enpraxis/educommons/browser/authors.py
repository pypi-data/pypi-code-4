from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AuthorsViewlet(ViewletBase):
    """Viewlet that displays the authors of the content"""

    index = ViewPageTemplateFile('authors.pt')

    def update(self):
        """Update"""
        super(AuthorsViewlet, self).update()
        if getattr(self.context, 'Creators', None):
            self.authors = self.context.Creators()
        else:
            self.authors = []

    def numCreators(self):
        """Number of creators"""
        return len(self.authors)

    def getCreators(self):
        """Get the current creators and return in a string separated
        by commas
        """
        return ', '.join(self.authors)


