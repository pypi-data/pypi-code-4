# -*- coding: utf-8 -*-

"""

    importer: mixpanel tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    this module tests ``Mixpanel``-specific provider functionality.

"""

# stdlib
import time
import json
import base64
import random
import unittest
import datetime

# importer
from importer import mix

# mixpanel constants
from importer.mix import _MIXPANEL_API
from importer.mix import _MIXPANEL_EXPORT

# main mixpanel-related classes
from importer.mix import Mixpanel
from importer.mix import MixpanelUploader
from importer.mix import MixpanelDownloader


## MixpanelTests - tests general integration with Mixpanel.
class MixpanelTests(unittest.TestCase):

    ''' Tests the ``Mixpanel`` provider class, which is
    	exposed at :py:class:`mix.Mixpanel`. '''

    random_ts = lambda self: datetime.datetime.fromtimestamp(random.randint(1377605000, 1377895000))

    def _valid_mixpanel_provider(self, instance=False, params=False):  # pragma: nocover

        ''' Tests the ``Mixpanel`` provider class, which is
            exposed at :py:class:`mix.Mixpanel`. '''

        ## `_request` shim
        def _request(self, methods, params={}):

            ''' Shim for submitting API requests to
                ``Mixpanel``. Returns ``self`` for
                chainability/introspection, unless
                the ``methods`` list contains 'export',
                in which case a fake export is mocked
                and returned. '''

            self.mock_request = (methods, params)
            if 'export' in methods:
                return "\n".join([
                    json.dumps({'event':'sample_kind','properties':{
                        'time': int(time.mktime(self.random_ts().timetuple())),
                        'blabs': True
                    }}),
                    json.dumps({'event':'sample_kind','properties':{
                        'time': int(time.mktime(self.random_ts().timetuple())),
                        'bleebs': True
                    }}),
                    ''  # throw in an extra line to try and juke the downloader
                ])  # return sample events

            return self  # otherwise return `self`

        ## `_library` shim
        def _library(self, api_key, api_secret):

            ''' Shim for constructing the API layer
                for ``Mixpanel``. Returns ``self`` for
                chainability/introspection. '''

            self.api_key = api_key
            self.api_secret = api_secret
            return self

        _bus_, _name_, _library_, _adapters_, _config_ = (
            object(),  # bus mock
            'MIXPANEL',  # provider name
            type('MixpanelMock', (object,), {
                'request': _request,  # request shim
                'api_key': None,  # fake API key
                'api_secret': None,  # fake API Secret
                'mock_request': None,  # fake request
                'Mixpanel': _library,  # fake constructor
                'random_ts': self.random_ts  # random timestamp lambda
            })(),  # library mock
            (MixpanelUploader, MixpanelDownloader),
            {
                'api_key': '_api_key_',  # mock mixpanel API key
                'api_secret': '_api_secret_'  # mock mixpanel API secret
            }
        )

        if instance:
            m = Mixpanel(_bus_, _name_, _library_, _adapters_, **_config_)
            if params:
                return (_bus_, _name_, _library_, _adapter_, _config_), m
            return m
        if params:
            return (_bus_, _name_, _library_, _adapters_, _config_), Mixpanel
        return Mixpanel

    def test_mixpanel_construct(self):

        ''' Test the :py:class:`Mixpanel` class, which
            implements the :py:class:`Provider`
            interface. '''

        _mixpanel_args, MixpanelProvider = self._valid_mixpanel_provider(instance=False, params=True)
        _bus, _name, _library, _adapters, _config = _mixpanel_args

        # try to construct without adapters
        with self.assertRaises(TypeError):
            MixpanelProvider(_bus, _name, _library, tuple(), **_config)

        # try to construct with incomplete adapters
        with self.assertRaises(TypeError):
            MixpanelProvider(_bus, _name, _library, (MixpanelUploader,), **_config)

        # try to construct in a valid way
        _valid_mixpanel = MixpanelProvider(_bus, _name, _library, _adapters, **_config)

        # test attached parameters
        self.assertNotEqual(_valid_mixpanel.timezone, None)

        # test attached API key and API secret
        self.assertEqual(_valid_mixpanel.lib.api_key, '_api_key_')
        self.assertEqual(_valid_mixpanel.lib.api_secret, '_api_secret_')

    def test_mixpanel_config(self):

        ''' Test :py:attr:`Mixpanel.config`, which exposes
            ``Mixpanel``-related provider config listed in
            *importer's* ``config.json``. '''

        _mixpanel_provider = self._valid_mixpanel_provider(instance=True)

        # check values from config
        self.assertIsInstance(_mixpanel_provider.config, dict)
        self.assertEqual(_mixpanel_provider.config.get('api_key'), '_api_key_')
        self.assertEqual(_mixpanel_provider.config.get('api_secret'), '_api_secret_')

    def test_mixpanel_toggle_export(self):

        ''' Test :py:attr:`Mixpanel` with Python's ``with``
            protocol, applied in this case to seamlessly
            switch the API endpoint used by ``Mixpanel``,
            which must be done when exporting versus
            importing events. '''

        _mixpanel_provider = self._valid_mixpanel_provider(instance=True)

        # should start at regular API enpdoint
        self.assertEqual(_mixpanel_provider.client.ENDPOINT, _MIXPANEL_API)

        # with blocks should properly re-raise exceptions
        with self.assertRaises(RuntimeError):

            with _mixpanel_provider:

                # should now be the export API enpdoint
                self.assertEqual(_mixpanel_provider.client.ENDPOINT, _MIXPANEL_EXPORT)
                raise RuntimeError('this should bubble up')

        self.assertEqual(_mixpanel_provider.client.ENDPOINT, _MIXPANEL_API)


## MixpanelUploaderTests - tests the :py:class:`MixpanelUploader`.
class MixpanelUploaderTests(MixpanelTests):

    ''' Tests the ``Mixpanel`` uploader class, which is
    	exposed at :py:class:`mix.MixpanelUploader`. '''

    def test_mixpanel_upload(self):

        ''' Test the :py:meth:`upload` method on the uploader
            for ``Mixpanel``, exposed at :py:class:`mix.MixpanelUploader`. '''

        _mixpanel_provider = self._valid_mixpanel_provider(instance=True)

        # check uploader cached access
        uploader = _mixpanel_provider.uploader
        c_uploader = _mixpanel_provider.uploader
        self.assertEqual(uploader, c_uploader)

        # make some sample events
        event_1 = 'sample_kind', {'blab': True}, None
        event_2 = 'sample_kind', {'bleebs': True}, datetime.datetime.fromtimestamp(random.randint(1377605000, 1377895000))
        event_3 = 'sample_kind2', {'blops': True}, datetime.datetime.now()

        for kind, event, timestamp in (event_1, event_2, event_3):
            _mixpanel_provider.uploader.upload(kind, json.dumps(event), mix._TO_MIXPANEL_DATE(timestamp) if timestamp else None)

        # check event kind existence
        self.assertTrue('sample_kind' in _mixpanel_provider.uploader.events_by_kind)
        self.assertTrue('sample_kind2' in _mixpanel_provider.uploader.events_by_kind)

        # check event kind length
        self.assertEqual(len(_mixpanel_provider.uploader.events_by_kind['sample_kind']), 2)
        self.assertEqual(len(_mixpanel_provider.uploader.events_by_kind['sample_kind2']), 1)

        return _mixpanel_provider

    def test_mixpanel_upload_commit(self):

        ''' Test the :py:meth:`commit` method on the uploader
            for ``Mixpanel``, exposed at :py:class:`mix.MixpanelUploader`. '''

        # bad form but why not: grab previous mixpanel provider
        _mixpanel_provider = self._valid_mixpanel_provider(instance=True)

        # make sure events are still there
        self.assertEqual(len(_mixpanel_provider.uploader.events_by_kind.keys()), 2)
        self.assertEqual(len(_mixpanel_provider.uploader.events_by_kind['sample_kind']), 2)
        self.assertEqual(len(_mixpanel_provider.uploader.events_by_kind['sample_kind2']), 1)

        # commit, see what happens
        count = _mixpanel_provider.uploader.commit()
        self.assertEqual(count, 3)

        # make sure there's a request
        self.assertNotEqual(_mixpanel_provider.client.mock_request, None)


## MixpanelDownloaderTests - tests the :py:class:`MixpanelDownloader`.
class MixpanelDownloaderTests(MixpanelTests):

    ''' Tests the ``Mixpanel`` downloader class, which is
    	exposed at :py:class:`mix.MixpanelDownloader`. '''

    def test_mixpanel_download(self):

        ''' Test the :py:meth:`upload` method on the downloader
            for ``Mixpanel``, exposed at :py:class:`mix.MixpanelUploader`. '''

        _mixpanel_provider = self._valid_mixpanel_provider(instance=True)

        # check downloader cached access
        downloader = _mixpanel_provider.downloader
        c_downloader = _mixpanel_provider.downloader
        self.assertEqual(downloader, c_downloader)

        # manufacture start and end datetimes
        start, end = (
            datetime.datetime(year=2013, month=8, day=20, hour=12, minute=0, second=0),
            datetime.datetime(year=2013, month=8, day=30, hour=12, minute=0, second=0)
        )

        # try to download events via generator
        events = []
        for kind, deserialized, timestamp in _mixpanel_provider.downloader.download(start, end, ['sample_kind']):

            # check types
            self.assertIsInstance(kind, basestring)
            self.assertIsInstance(deserialized, dict)
            self.assertIsInstance(timestamp, datetime.datetime)

            # check values
            self.assertEqual(kind, 'sample_kind')

            # add to events
            events.append((kind, deserialized, timestamp))

        # check length of yielded events
        self.assertEqual(len(events), 2)
