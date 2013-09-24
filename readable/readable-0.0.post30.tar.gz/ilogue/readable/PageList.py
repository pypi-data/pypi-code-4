from bs4 import BeautifulSoup
from ilogue.readable.matcher import Matcher


class PageList(object):

    def __init__(self, stringContent):
        self.listSoup = BeautifulSoup(stringContent)
        self.items = self.listSoup.findAll('html:li')


    def withLength(self, expLength):
        actLength = len(self.items)
        if not actLength == expLength:
            msg = 'PageList length was {0}, not {1}.'
            raise AssertionError(msg.format(actLength, expLength))
        return self

    def withAnItem(self, expected):
        for item in self.items:
            if self._itemMatches(item, expected):
                break;
        else:
            msg = 'No item in the list matched: {0}.'
            raise AssertionError(msg.format(str(expected)))
        return self

    def _itemMatches(self, item, expected):
        if isinstance(expected, Matcher):
            itemContents = str(item.renderContents())
            return expected.matches(itemContents)
        else:
            raise ValueError('Can only match Matcher objects to PageList items.')
