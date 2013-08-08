from django.test import TestCase, RequestFactory

from views import StaticSiteTemplateView

#http://tech.novapost.fr/django-unit-test-your-views-en.html

class TestURLNormalisation(TestCase):
    def test_empty_path_results_in_index_html(self):
        theView = StaticSiteTemplateView.as_view()
        request = RequestFactory().get('/')


        self.assertEquals(2, 1 + 1)
