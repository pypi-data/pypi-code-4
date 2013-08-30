import unittest

import mock


settings = """[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 5000
[app:main]
use = call:%s:main
facebook.app_id = 123
facebook.secret_key = abcdef1234567890
facebook.namespace = test_canvas
facebook.scope =
facebook.rt-subscriptions =
    user = name, friends
    payments = actions, disputes""" % __name__


def main(global_config, **settings):
    from pyramid.config import Configurator
    config = Configurator(settings=settings)
    config.include('pyramid_facebook')
    return config.make_wsgi_app()


class TestManageSubscriptions(unittest.TestCase):

    def _get_command(self, *params):
        from pyramid_facebook.real_time import ManageSubscriptions
        return ManageSubscriptions(params)

    def _get_subscriptions_list(self):
        return {
            'data': [
                {'active': True,
                 'fields': ['friends', 'name'],
                 'object': 'user',
                 'callback_url': 'http://example.com/test_canvas/real-time',
                 },
                {'active': True,
                 'fields': ['actions', 'disputes'],
                 'object': 'payments',
                 'callback_url': 'http://example.com/test_canvas/real-time'
                 },
            ]}

    def setUp(self):
        self.patch_open = mock.patch('paste.deploy.loadwsgi.open',
                                     mock_open(read_data=settings),
                                     create=True)
        self.patch_open.start()

        self.patch_graph_api = mock.patch('pyramid_facebook.real_time.'
                                          'GraphAPI')

        self.patch_get_app_token = mock.patch('pyramid_facebook.real_time.'
                                              'get_application_access_token')

        self.patch_list = mock.patch('pyramid_facebook.real_time.'
                                     'list_real_time_subscriptions')

        self.m_graph_api = self.patch_graph_api.start()

        self.m_list = self.patch_list.start()

        self.m_list.return_value = self._get_subscriptions_list()

        self.patch_get_app_token.start().return_value = 'app_token'

    def tearDown(self):
        self.patch_open.stop()
        self.patch_graph_api.stop()
        self.patch_list.stop()
        self.patch_get_app_token.stop()

    def test_list(self):
        ms = self._get_command('fake.ini', 'list')
        ms.run()

    def test_update(self):
        ms = self._get_command('fake.ini', 'update', 'user=name,friends')
        ms.run()

    def test_delete(self):
        ms = self._get_command('fake.ini', 'delete')
        ms.run()

    def test_setup(self):
        ms = self._get_command('fake.ini', 'setup')
        ms.run()

    @mock.patch('pyramid_facebook.real_time.sys')
    def test_command_line_script(self, m_sys):
        from pyramid_facebook.real_time import command_line_script
        m_sys.argv = ['pfacebook-real-time', 'fake.ini', 'list']
        command_line_script()


def mock_open(read_data):
    """Mock module does not mock readline and readlines method on file object.
    Unfortunately config parser called when boostraping the app uses readline.
    """
    mock_obj = mock.MagicMock(name='open', spec=open)
    handle = mock.MagicMock(spec=file)
    handle.__enter__.return_value = handle
    handle.read.return_value = read_data

    class ReadLineMock():
        def __init__(self, read_data):
            self.read_data = read_data.split('\n')

        def next(self):
            if self.read_data:
                return self.read_data.pop(0)
            return ''

    handle.readline.side_effect = ReadLineMock(read_data)
    mock_obj.return_value = handle
    return mock_obj
