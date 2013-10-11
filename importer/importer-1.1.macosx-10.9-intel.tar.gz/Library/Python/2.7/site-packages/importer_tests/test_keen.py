# -*- coding: utf-8 -*-

'''

    importer: keen tests
    ~~~~~~~~~~~~~~~~~~~~

    this module tests ``Keen``-specific provider functionality.

    :author: Sam Gammon <sam@keen.io>
    :license: This software follows the MIT (OSI-approved)
              license for open source software. A truncated
              version is included here; for full licensing
              details, see ``LICENSE.md`` in the root directory
              of the project.

              Copyright (c) 2013, Keen IO

              The above copyright notice and this permission notice shall be included in
              all copies or substantial portions of the Software.

              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
              THE SOFTWARE.

'''


# stdlib
import json
import time
import random
import unittest
import datetime

# importer
from importer import mix

# main keen-related classes
from importer.mix import Keen
from importer.mix import KeenUploader
from importer.mix import KeenDownloader


## KeenTests - tests general integration with Keen.
class KeenTests(unittest.TestCase):

    ''' Tests the ``Keen`` provider class, which is
        exposed at :py:class:`mix.Keen`. '''

    def _valid_keen_provider(self, instance=False, params=False):  # pragma: nocover

        ''' Generate a valid :py:class:`Keen` provider
            object, with minimal config/etc for use
            in testing. '''

        ## `add_events` shim
        def _add_events(self, events):

            ''' Quick shim to simulate a mocked ``Keen``
                library, supporting batch event writes. '''

            self.events_cache = events
            return self

        ## `extraction` shim
        def _extraction(self, kind, range):

            ''' Quick shim to simulate a mocked ``Keen``
                library, supporting event extractions. '''

            # manufacture known datetimes
            dt = datetime.datetime(year=2013, month=8, day=24, hour=12, minute=30, second=0)
            dt2 = datetime.datetime(year=2013, month=8, day=25, hour=12, minute=35, second=0)
            
            return [
                {'kind': kind, 'prop': 123, 'keen': {'timestamp': mix._TO_KEEN_DATE(dt)}},
                {'kind': kind, 'prop': 124, 'keen': {'timestamp': mix._TO_KEEN_DATE(dt2)}}
            ]

        ## prepare args
        _bus_, _name_, _library_, _adapters_, _config_ = (
            object(),  # bus mock
            'KEEN',  # provider name
            type('KeenMock', (object,), {
                'project_id': None,
                'read_key': None,
                'write_key': None,
                'add_events': _add_events,
                'extraction': _extraction,
                'events_cache': None})(),  # library mock
            (KeenUploader, KeenDownloader),  # bound adapters
            {
                'read_key': '__read_key__',
                'write_key': '__write_key__',
                'project_id': '__project_id__'
            }
        )

        if instance:
            k = Keen(_bus_, _name_, _library_, _adapters_, **_config_)
            if params:
                return (_bus_, _name_, _library_, _adapters_, _config_), k
            return k
        if params:
            return (_bus_, _name_, _library_, _adapters_, _config_), Keen
        return Keen

    def test_keen_construct(self):

        ''' Test the :py:class:`Keen` class, which
            implements the :py:class:`Provider`
            interface. '''

        _keen_args, KeenProvider = self._valid_keen_provider(instance=False, params=True)
        _bus, _name, _library, _adapters, _config = _keen_args

        # try to construct without adapters
        with self.assertRaises(TypeError):
            KeenProvider(_bus, _name, _library, tuple(), **_config)

        # try to construct with incomplete adapters
        with self.assertRaises(TypeError):
            KeenProvider(_bus, _name, _library, (KeenUploader,), **_config)

        # try to construct in a valid way
        _valid_keen = KeenProvider(_bus, _name, _library, _adapters, **_config)

        # test attached parameters
        self.assertEqual(_valid_keen.bus, _bus)
        self.assertEqual(_valid_keen.lib, _library)
        self.assertEqual(_valid_keen.name, 'KEEN')
        self.assertIsInstance(_valid_keen.adapters, tuple)
        self.assertEqual(len(_valid_keen.adapters), 2)

    def test_keen_config(self):

        ''' Test :py:attr:`Keen.config`, which exposes
            ``Keen``-related provider config listed in
            *importer's* ``config.json``. '''

        _keen_provider = self._valid_keen_provider(instance=True)

        # check config values sent in by the valid provider util
        self.assertIsInstance(_keen_provider.config, dict)
        self.assertEqual(_keen_provider.config['read_key'], '__read_key__')
        self.assertEqual(_keen_provider.config['write_key'], '__write_key__')
        self.assertEqual(_keen_provider.config['project_id'], '__project_id__')

    def test_keen_key_methods(self):

        ''' Test utility methods exposed on :py:class:`Keen`
            that allow direct API users to change/set
            their config values (``project_id``, ``read_key``,
            and ``write_key``) in-flight. '''

        _keen_provider = self._valid_keen_provider(instance=True)

        # check getter methods, implicitly
        self.assertEqual(_keen_provider.read_key, _keen_provider.config['read_key'])
        self.assertEqual(_keen_provider.write_key, _keen_provider.config['write_key'])
        self.assertEqual(_keen_provider.project_id, _keen_provider.config['project_id'])

        # check getter methods, explicitly
        self.assertEqual(_keen_provider._get_read_key(), _keen_provider.config['read_key'])
        self.assertEqual(_keen_provider._get_write_key(), _keen_provider.config['write_key'])
        self.assertEqual(_keen_provider._get_project_id(), _keen_provider.config['project_id'])

        # check setter methods, implicitly
        _keen_provider.project_id = 'supguyz'
        self.assertEqual(_keen_provider.project_id, 'supguyz')
        self.assertEqual(_keen_provider.config['project_id'], 'supguyz')

        _keen_provider.read_key = 'readkey_sample'
        self.assertEqual(_keen_provider.read_key, 'readkey_sample')
        self.assertEqual(_keen_provider.config['read_key'], 'readkey_sample')

        _keen_provider.write_key = 'writekey_sample'
        self.assertEqual(_keen_provider.write_key, 'writekey_sample')
        self.assertEqual(_keen_provider.config['write_key'], 'writekey_sample')

        # check setter methods, explicitly
        _keen_provider._set_project_id('supguyz2')
        self.assertEqual(_keen_provider.project_id, 'supguyz2')
        self.assertEqual(_keen_provider.config['project_id'], 'supguyz2')

        _keen_provider._set_read_key('readkey_sample2')
        self.assertEqual(_keen_provider.read_key, 'readkey_sample2')
        self.assertEqual(_keen_provider.config['read_key'], 'readkey_sample2')

        _keen_provider._set_write_key('writekey_sample2')
        self.assertEqual(_keen_provider.write_key, 'writekey_sample2')
        self.assertEqual(_keen_provider.config['write_key'], 'writekey_sample2')

        # try to set an invalid config item
        with self.assertRaises(ValueError):
            _keen_provider._set_config('invalid_config', True)


## KeenUploaderTests - tests the :py:class:`KeenUploader`.
class KeenUploaderTests(KeenTests):

    ''' Tests the ``Keen`` uploader class, which is
        exposed at :py:class:`mix.KeenUploader`. '''

    def test_keen_upload(self):

        ''' Test the :py:meth:`upload` method on the uploader
            for ``Keen``, exposed at :py:class:`mix.KeenUploader`. '''

        _keen_provider = self._valid_keen_provider(instance=True)

        # check uploader cached access
        uploader = _keen_provider.uploader
        c_uploader = _keen_provider.uploader
        self.assertEqual(uploader, c_uploader)

        # make sure events are empty
        _keen_provider.uploader.events_by_kind = {}

        # make some sample events
        event_1 = 'sample_kind', {'blab': True}, None
        event_2 = 'sample_kind', {'bleebs': True}, mix.timezone('UTC').localize(datetime.datetime.fromtimestamp(random.randint(1377605000, 1377895000)))
        event_3 = 'sample_kind2', {'blops': True}, mix.timezone('UTC').localize(datetime.datetime.now())

        for kind, event, timestamp in (event_1, event_2, event_3):
            _keen_provider.uploader.upload(kind, json.dumps(event), timestamp if timestamp is not None else None)

        # check event kind existence
        self.assertTrue('sample_kind' in _keen_provider.uploader.events_by_kind)
        self.assertTrue('sample_kind2' in _keen_provider.uploader.events_by_kind)

        # check event kind length
        self.assertEqual(len(_keen_provider.uploader.events_by_kind['sample_kind']), 2)
        self.assertEqual(len(_keen_provider.uploader.events_by_kind['sample_kind2']), 1)

    def test_keen_upload_commit(self):

        ''' Test the :py:meth:`commit` method on the uploader
            for ``Keen``, exposed at :py:class:`mix.KeenUploader`. '''

        _keen_provider = self._valid_keen_provider(instance=True)

        # make sure events are empty
        _keen_provider.uploader.events_by_kind = {}

        # make some sample events
        event_1 = 'sample_kind', {'blab': True}, None
        event_2 = 'sample_kind', {'bleebs': True}, mix.timezone('UTC').localize(datetime.datetime.fromtimestamp(random.randint(1377605000, 1377895000)))
        event_3 = 'sample_kind2', {'blops': True}, mix.timezone('UTC').localize(datetime.datetime.now())

        for kind, event, timestamp in (event_1, event_2, event_3):
            _keen_provider.uploader.upload(kind, json.dumps(event), timestamp if timestamp is not None else None)

        # dispatch `commit`
        count = _keen_provider.uploader.commit()

        # make sure count matches
        self.assertEqual(count, 3)
        self.assertIsInstance(_keen_provider.lib.events_cache, dict)
        self.assertTrue('sample_kind' in _keen_provider.lib.events_cache)
        self.assertTrue('sample_kind2' in _keen_provider.lib.events_cache)
        self.assertEqual(len(_keen_provider.lib.events_cache['sample_kind']), 2)
        self.assertEqual(len(_keen_provider.lib.events_cache['sample_kind2']), 1)


## KeenDownloaderTests - tests the :py:class:`KeenDownloader`.
class KeenDownloaderTests(KeenTests):

    ''' Tests the ``Keen`` downloader class, which is
        exposed at :py;class:`mix.KeenDownloader`. '''

    def test_keen_download(self):

        ''' Test the :py:meth:`upload` method on the downloader
            for ``Keen``, exposed at :py:class:`mix.KeenUploader`. '''

        _keen_provider = self._valid_keen_provider(instance=True)

        # check downloader cached access
        downloader = _keen_provider.downloader
        c_downloader = _keen_provider.downloader
        self.assertEqual(downloader, c_downloader)

        # manufacture start and end datetimes
        start, end = (
            datetime.datetime(year=2013, month=8, day=20, hour=12, minute=0, second=0),
            datetime.datetime(year=2013, month=8, day=30, hour=12, minute=0, second=0)
        )

        # try to download events via generator
        events = []
        for kind, deserialized, timestamp in _keen_provider.downloader.download(start, end, ['sample_kind']):

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
