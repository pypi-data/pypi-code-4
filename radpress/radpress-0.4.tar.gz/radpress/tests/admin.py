from django.core.urlresolvers import reverse
from radpress.tests.base import RadpressTestCase
from radpress.readers import get_reader_initial
from radpress.settings import DEFAULT_MARKUP


class AdminTest(RadpressTestCase):

    def setUp(self):
        super(AdminTest, self).setUp()

        self.client.login(username=self.user1.username, password='secret')

    def test_open_article_add_and_check_initial_data(self):
        url = reverse('admin:radpress_article_add')
        initial_content = get_reader_initial(markup=DEFAULT_MARKUP)
        response = self.client.get(url)
        self.assertIn(initial_content, response.content)
