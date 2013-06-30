from radpress.tests.base import RadpressReaderTestCase


class MarkdownTest(RadpressReaderTestCase):
    markup = 'markdown'
    file_path = 'test_content.md'

    def test_codehilite(self):
        self.assertIn('<div class="codehilite">', self.content_body)
        self.assertIn(
            '<table class="codehilitetable"><tr><td class="linenos">',
            self.content_body)
