"""
    type specific test based on spoke base tests
"""
from wheelcms_axle.tests.test_spoke import BaseSpokeTest, BaseSpokeTemplateTest
from wheelcms_spokes.news import NewsType, News
from wheelcms_axle.tests.test_impexp import BaseSpokeImportExportTest
from wheelcms_axle.tests.test_search import BaseTestSearch

class TestNewsSpokeTemplate(BaseSpokeTemplateTest):
    """ Test the News type """
    type = NewsType

    def valid_data(self):
        """ return additional data for News validation """
        return dict(intro="Hi There!", body="Hello World")

class TestNewsSpoke(BaseSpokeTest):
    """ Test the News type """
    type = NewsType

class TestNewsSpokeImpExp(BaseSpokeImportExportTest):
    type = News
    spoke = NewsType

class TestNewsSpokeSearch(BaseTestSearch):
    type = NewsType
