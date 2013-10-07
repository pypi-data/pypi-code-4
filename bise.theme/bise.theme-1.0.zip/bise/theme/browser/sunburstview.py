from zope.component import getMultiAdapter
from plonetheme.sunburst.browser.interfaces import ISunburstView
from plonetheme.sunburst.browser.sunburstview import SunburstView as Base
from zope.interface import implements


class SunburstView(Base):
    implements(ISunburstView)

    def getColumnsClasses(self, view=None):
        """Determine whether a column should be shown. The left column is
        called plone.leftcolumn; the right column is called plone.rightcolumn.
        """

        plone_view = getMultiAdapter(
            (self.context, self.request), name=u'plone')
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')

        sl = plone_view.have_portlets('plone.leftcolumn', view=view);
        sr = plone_view.have_portlets('plone.rightcolumn', view=view);

        isRTL = portal_state.is_rtl()

        # pre-fill dictionary
        columns = dict(one="", content="", two="")

        if not sl and not sr:
            # we don't have columns, thus conten takes the whole width
            columns['content'] = "width-full position-0"

        elif sl and sr:
            columns['one'] = "width-3 position-0"
            columns['content'] = "width-10 position-3"
            columns['two'] = "width-3 position-13"

        elif (sr and not sl) and isRTL:
            columns['content'] = "width-13 position-3"
            columns['two'] = "width-3 position-0"

        elif (sr and not sl) and not isRTL:
            columns['content'] = "width-13 position-0"
            columns['two'] = "width-3 position-13"

        elif (sl and not sr) and isRTL:
            columns['one'] = "width-3 position-13"
            columns['content'] = "width-13 position-0"

        elif (sl and not sr) and not isRTL:
            columns['one'] = "width-3 position-0"
            columns['content'] = "width-13 position-3"

        # append cell to each css-string
        for key, value in columns.items():
            columns[key] = "cell " + value

        return columns
