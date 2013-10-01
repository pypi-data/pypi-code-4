# -*- coding: utf-8 -*-
import unittest

import mock


class TestPyramidFacebook(unittest.TestCase):

    def test_includeme(self):
        settings = {
            'facebook.namespace': 'namespace',
            'facebook.secret_key': 'secret_key',
            }

        config = mock.Mock()
        config.registry.settings = settings

        # TEST includeme
        from pyramid_facebook import includeme
        self.assertIsNone(includeme(config))

        self.assertEqual(10, config.include.call_count)
        prefix = '/namespace'

        self.assertEqual([
            mock.call('pyramid_contextauth'),
            mock.call('pyramid_facebook.predicates', route_prefix=prefix),
            mock.call('pyramid_facebook.security', route_prefix=prefix),
            mock.call('pyramid_facebook.auth', route_prefix=prefix),
            mock.call('pyramid_facebook.canvas', route_prefix=prefix),
            mock.call('pyramid_facebook.utility', route_prefix=prefix),
            mock.call('pyramid_facebook.credits', route_prefix=prefix),
            mock.call('pyramid_facebook.real_time', route_prefix=prefix),
            mock.call('pyramid_facebook.opengraph', route_prefix=prefix),
            mock.call('pyramid_facebook.payments', route_prefix=prefix),
        ],
            config.include.call_args_list)

    def test_includeme_exception(self):
        from pyramid_facebook import includeme
        bad_settings = {}

        config = mock.MagicMock()
        config.registry.settings = bad_settings

        self.assertRaises(KeyError, includeme, config)

        bad_settings = {
            'facebook.secret_key': 'secret_key',
        }

        config.registry.settings = bad_settings
        self.assertRaises(KeyError, includeme, config)
