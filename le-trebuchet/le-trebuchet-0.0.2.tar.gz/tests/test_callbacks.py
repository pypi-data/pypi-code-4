import unittest
from mock import patch, Mock

from trebuchet.lib.callbacks import do_web_callback


class WebCallbackTest(unittest.TestCase):

    @patch('requests.post', return_value=Mock(status_code=200))
    def test_case(self, mock_requests_post):
        mock_pkg = Mock(full_package_name='dh-foo', version='1.0.0', final_deb_name='dh-foo-1.0.0-amd64.deb')

        response = do_web_callback("http://example.com/add_to_stack/123/", mock_pkg)
        self.assertEquals(response, True)


if __name__ == '__main__':
    unittest.main()