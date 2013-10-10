# -*- coding: utf-8 -*-

"""

    importer: tests
    ~~~~~~~~~~~~~~~

    this module provides tests for the main ``importer``
    business logic module, provided at :py:mod:`importer.mix`.

"""

# stdlib
import sys
import logging
import unittest
import datetime

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

# tests
from importer_tests import test_keen
from importer_tests import test_mixpanel

# importer
from importer import tz
from importer import mix
from importer import __main__ as main

# main classes
from importer.mix import Importer
from importer.mix import Adapter
from importer.mix import Provider


## Globals
_MINIMAL_OUTPUT = '[importer]: Beginning event data download...\n[importer]: Beginning event data upload...\n[importer]: Committing events...\n[importer]: Upload complete.\n[importer]: Done, exiting `Importer`.\n'


## UtilTests - tests small utilities and lambdas provided by :py:mod:`mix`.
class UtilTests(unittest.TestCase):

    ''' Tests utility classes, lambdas, globals
        and functions. Random small stuff for
        format conversion and plumbing like that. '''

    def test_exports(self):

        ''' Tests that lambdas and constants bound
            at :py:mod:`importer.mix`'s top level
            exist and are accessible as attributes. '''

        for export in frozenset((

            # CSV-related globals
            '_CSV_FILE',  # file to output CSV buffer to
            '_CSV_PARAMS',  # config for :py:mod:`csv`

            # Mixpanel-related lambdas
            '_MIXPANEL_DATE_FMT',  # mixpanel's date format (YYYY-MM-DD)
            '_MIXPANEL_API',  # mixpanel's regular API endpoint
            '_MIXPANEL_EXPORT',  # mixpanel's export API endpoint

            # Keen-related lambdas
            '_KEEN_DATE_FMT',  # regular date format for keen (without TZ, for ``strptime``)
            '_KEEN_DATE_FMT_ISO',  # ISO8601 date format for keen (with TZ, for ``strftime``)

            '_PROVIDER',  # small lambda that resolves providers by name (for instance, _PROVIDER('keen'))
            '_PROVIDER_IMPL',  # small lambda that resolves a provider class by name, instead of a sentinel

            '_PRETTY_DATE',  # small lambda that formats a date in a pretty human-readable way
            '_TO_KEEN_DATE',  # formats a python ``datetime`` as a Keen-style ISO8601 timestamp
            '_FROM_KEEN_DATE',  # parses a Keen-style ISO8601 timestamp into a python ``datetime``
            '_TO_MIXPANEL_DATE',  # formats a python ``datetime`` as a Mixpanel-style timestamp (YYYY-MM-DD)
            '_FROM_MIXPANEL_DATE')):  # parses a Mixpanel-style timestamp into a python ``datetime``

            self.assertTrue(hasattr(mix, export))

    def test_mixpanel_constants(self):

        ''' Thorougly tests Mixpanel-related constants
            bound at :py:mod:`importer.mix`'s top level. '''

        ## == _MIXPANEL_DATE_FMT == ##

        # simple format test
        dt_now = datetime.datetime.now()
        dt_converted = datetime.datetime.strptime(dt_now.strftime(mix._MIXPANEL_DATE_FMT), mix._MIXPANEL_DATE_FMT)

        # drop resolution from `dt_now` and compare
        dt_now = datetime.datetime.combine(dt_now.date(), datetime.time(hour=0, minute=0))
        self.assertEqual(dt_now, dt_converted)  # check equality

        # try to unpack strings
        sample_valid, sample_invalid = '2013-01-05', '05-01-2013'

        # check valid date
        valid_dt = datetime.datetime.strptime(sample_valid, mix._MIXPANEL_DATE_FMT)
        self.assertEqual(valid_dt.year, 2013)
        self.assertEqual(valid_dt.month, 01)
        self.assertEqual(valid_dt.day, 5)

        # make sure we have our exceptions right
        with self.assertRaises(ValueError):
            invalid_dt = datetime.datetime.strptime(sample_invalid, mix._MIXPANEL_DATE_FMT)

        ## == _MIXPANEL_API / _MIXPANEL_EXPORT == ##

        # test regular endpoint
        self.assertIsInstance(mix._MIXPANEL_API, basestring)
        self.assertTrue('mixpanel.com' in mix._MIXPANEL_API)

        # test export endpoint
        self.assertIsInstance(mix._MIXPANEL_EXPORT, basestring)
        self.assertTrue('data.mixpanel.com' in mix._MIXPANEL_EXPORT)

    def test_keen_constants(self):
    
        ''' Thoroughly tests Keen-related constants
            bound at :py:mod:`importer.mix`'s top level. '''
    
        # sample DT
        sample = mix.timezone('UTC').localize(datetime.datetime(year=2013, month=8, day=24, hour=12, minute=30, second=01))

        # test extraction of a keen date
        sample_keen = mix._TO_KEEN_DATE(sample)

        # test formatting as a keen date
        interpreted_sample = mix._FROM_KEEN_DATE(sample_keen)

        # compare
        self.assertEqual(sample, interpreted_sample)

    def test_totimestamp(self):

        ''' Tests the top-level :py:func:`_TO_TIMESTAMP`
            lambda, which resolves an integer timestamp,
            given a Python :py:class:`datetime.datetime`. '''

        # setup known datetime and timestamp
        ts, dt = 1377372600, datetime.datetime(year=2013, month=8, day=24, hour=12, minute=30, second=0)
        self.assertEqual(ts, mix._TO_TIMESTAMP(dt))

    def test_provider_lambda(self):
    
        ''' Tests the top-level :py:func:`_PROVIDER`
            lambda, which resolves a provider by name. '''
    
        # make sure we can resolve keen
        self.assertEqual(mix.Providers.KEEN, 'KEEN')
        self.assertEqual(mix._PROVIDER('keen'), 'KEEN')
        self.assertEqual(mix._PROVIDER(mix.Providers.KEEN), 'KEEN')
        self.assertEqual(mix._PROVIDER_IMPL('KEEN'), mix.Keen)
        self.assertEqual(mix._PROVIDER_IMPL(mix.Providers.KEEN), mix.Keen)
        self.assertEqual(mix._PROVIDER_IMPL(mix._PROVIDER('keen')), mix.Keen)

        # make sure we can resolve mixpanel
        self.assertEqual(mix.Providers.MIXPANEL, 'MIXPANEL')
        self.assertEqual(mix._PROVIDER('mixpanel'), 'MIXPANEL')
        self.assertEqual(mix._PROVIDER(mix.Providers.MIXPANEL), 'MIXPANEL')
        self.assertEqual(mix._PROVIDER_IMPL('MIXPANEL'), mix.Mixpanel)
        self.assertEqual(mix._PROVIDER_IMPL(mix.Providers.MIXPANEL), mix.Mixpanel)
        self.assertEqual(mix._PROVIDER_IMPL(mix._PROVIDER('mixpanel')), mix.Mixpanel)

    def test_pretty_date(self):
    
        ''' Tests the top-level :py:func:`_PRETTY_DATE`
            lambda, which formats a date in a nice way. '''
    
        # try to format a known date in a pretty way
        x = datetime.datetime(year=2013, month=8, day=24, hour=12, minute=30)
        self.assertEqual(mix._PRETTY_DATE(x), 'Sat Aug 24, 2013')

    def test_mixpanel_lambdas(self):
    
        ''' Test Mixpanel-related lambdas, which are
            exposed at :py:func:`_TO_MIXPANEL_DATE`
            and :py:func:`_FROM_MIXPANEL_DATE`. '''
    
        # make a known date
        sample_mixpanel_dt = datetime.datetime(year=2013, month=8, day=24)

        # try using the mixpanel format
        mixpanel_fmt = sample_mixpanel_dt.strftime(mix._MIXPANEL_DATE_FMT)
        self.assertEqual(mixpanel_fmt, '2013-08-24')

        # try using the lambdas
        mixpanel_date = mix._FROM_MIXPANEL_DATE(mixpanel_fmt)
        self.assertTrue(sample_mixpanel_dt, mixpanel_date)

        # try a full deserialize->serialize
        self.assertTrue(sample_mixpanel_dt, mix._FROM_MIXPANEL_DATE(mix._TO_MIXPANEL_DATE(sample_mixpanel_dt)))


## ProviderTests - tests functionality related to abstract providers.
class ProviderTests(unittest.TestCase):

    ''' Tests the abstract provider class, which
        is exposed at :py:class:`mix.Provider`. '''

    @classmethod
    def _valid_provider(cls, instance=False, params=False, klass=True):  # pragma: nocover

        ''' Small utility method to generate a valid
            :py:class:`mix.Provider` implementation
            on-the-fly. '''

        # can only return an instance or params as 2nd pos value
        if instance and params: raise TypeError('you are doing it wrong')

        ## == Valid Provider == ##

        class ValidProvider(mix.Provider):

            ''' Sample (valid) provider implementation,
                tests ABC enforcement. '''

            def initialize(self):

                ''' Test initialization method, which is
                    enforced by the :py:class:`mix.Provider`
                    spec. '''

                return

        class ValidUploader(mix.Uploader):

            ''' Sample (valid) uploader implementation,
                for testing property access. '''

            def commit(self, *args, **kwargs):

                ''' Commit hook. Must be defined to
                    provide an uploader. '''

            def upload(self, *args, **kwargs):

                ''' Upload hook. Must be defined to
                    provide an uploader. '''

        class ValidDownloader(mix.Downloader):

            ''' Sample (valid) downloader implementation,
                for testing property access. '''

            def download(self):

                ''' Download hook. Must be defined to
                    provide a downloader. '''

        # provider obj
        _importer_, _name_, _library_, _adapters_, _config_ = (
            object(),
            'VALID',
            object(),
            (ValidUploader, ValidDownloader),
            {'sample_key': True}
        )

        if instance:
            if klass:
                return ValidProvider, ValidProvider(_importer_, _name_, _library_, _adapters_, **_config_)
            return ValidProvider(_importer_, _name_, _library_, _adapters_, **_config_)
        if params:
            if klass:
                return ValidProvider, (_importer_, _name_, _library_, _adapters_, _config_)
            return (_importer_, _name_, _library_, _adapters_, _config_)
        return ValidProvider

    def test_provider_abc(self):

        ''' Test Abstract Base Class semantics, against
            an invalid and valid :py:class:`mix.Provider`
            interface. '''

        ValidProvider = self._valid_provider(instance=False)

        # tests
        self.assertTrue(ValidProvider)  # is it there?
        self.assertIsInstance(ValidProvider, type)  # not a singleton?
        self.assertTrue(issubclass(ValidProvider, mix.Provider))  # inheritance

        ## == Invalid Provider == ##

        with self.assertRaises(TypeError):

            class InvalidProvider(mix.Provider):

                ''' Sample (invalid) provider implementation,
                    tests ABC enforcement. '''

                pass  # should have an ``initialize`` method

            invalid = InvalidProvider()  # should fail

    def test_provider_map(self):

        ''' Tests the top-level provider map, exported
            from :py:mod:`mix` as :py:class:`mix.Providers`. '''

        self.assertTrue(hasattr(mix, 'Providers'))  # class existence
        self.assertTrue(hasattr(mix.Providers, 'KEEN'))  # `KEEN` mapping
        self.assertTrue(hasattr(mix.Providers, 'MIXPANEL'))  # `MIXPANEL` mapping

    def test_provider_repr(self):

        ''' Tests :py:class:`Provider`'s ability to
            generate a nice string representation of
            itself. '''

        # test __repr__
        ValidProvider, _valid_provider = self._valid_provider(instance=True)
        self.assertEqual(_valid_provider.__repr__(), 'Provider(VALID)')

    def test_provider_workers(self):

        ''' Tests :py:class:`Provider`'s proxied lazy
            properties for accessing attached/bound
            :py:class:`Uploader` and :py:class:`Downloader`
            objects. '''

        ValidProvider, _params = self._valid_provider(params=True)
        _importer, _name, _library, _adapters, _config = _params

        # instantiate provider
        _provider = ValidProvider(*(_importer, _name, _library, _adapters), **_config)

        # up/downloader
        _up, _down = _adapters[0], _adapters[1]

        # test workers
        self.assertIsInstance(_provider.uploader, _up)
        self.assertIsInstance(_provider.uploader, _up)  # tests cached access
        self.assertIsInstance(_provider.uploader, mix.Uploader)
        self.assertIsInstance(_provider.downloader, _down)
        self.assertIsInstance(_provider.downloader, _down)  # tests cached access
        self.assertIsInstance(_provider.downloader, mix.Downloader)

    def test_provider_logging(self):

        ''' Tests the logging interface provided internally
            for :py:class:`Provider` implementors. '''

        ValidProvider, _valid_provider = self._valid_provider(instance=True)

        # make sure logging is there and looks like a logging pipe
        self.assertTrue(hasattr(_valid_provider.logging, 'debug'))
        self.assertTrue(hasattr(_valid_provider.logging, 'info'))
        self.assertTrue(hasattr(_valid_provider.logging, 'warning'))
        self.assertTrue(hasattr(_valid_provider.logging, 'error'))
        self.assertTrue(hasattr(_valid_provider.logging, 'critical'))


## AdapterTests - tests functionality related to abstract adapters.
class AdapterTests(unittest.TestCase):

    ''' Tests the abstract adapter class, which
        is exposed at :py:class:`mix.Adapter`. '''

    @classmethod
    def _valid_adapter(cls, uploader=False, downloader=True, instance=False):  # pragma: nocover

        ''' Acquire a valid :py:class:`Uploader`,
            :py:class:`Downloader`, or both. Whether
            an instance or class is returned is
            switchable via the kwarg ``instance``. '''

        _result = []

        if uploader:
            class ValidUploader(mix.Uploader):

                ''' Sample (valid) uploader implementation,
                    for testing property access. '''

                def commit(self, *args, **kwargs):

                    ''' Commit hook. Must be defined to
                        provide an uploader. '''

                def upload(self, *args, **kwargs):

                    ''' Upload hook. Must be defined to
                        provide an uploader. '''

            if instance:
                _result.append(ValidUploader(ProviderTests._valid_provider(instance=True, klass=False)))
            else:
                _result.append(ValidUploader)

        if downloader:
            class ValidDownloader(mix.Downloader):

                ''' Sample (valid) downloader implementation,
                    for testing property access. '''

                def download(self):

                    ''' Download hook. Must be defined to
                        provide a downloader. '''

            if instance:
                _result.append(ValidDownloader(ProviderTests._valid_provider(instance=True, klass=False)))
            else:
                _result.append(ValidDownloader)

        if _result:
            if len(_result) > 1:
                return tuple(_result)
            return _result[0]

    def test_adapter_direct_extend(self):

        ''' Make sure that new adapter types can't
            be added - only :py:class:`Uploader`
            and :py:class:`Downloader` may extend
            :py:class:`Adapter`. '''
    
        with self.assertRaises(RuntimeError):
            # try to extend :py:class:`Adapter` in an invalid way
            class SomeRandomAdapter(mix.Adapter):
                pass

    def test_adapter_direct(self):
    
        ''' Try directly instantiating a valid
            adapter, and handing it a mock
            :py:class:`Provider`. '''
    
        # try to instantiate abstract adapters directly
        with self.assertRaises(TypeError):
            mix.Adapter()
        with self.assertRaises(TypeError):
            mix.Uploader()
        with self.assertRaises(TypeError):
            mix.Downloader()

        # try instantiating a valid uploader/etc without a provider (direct)
        with self.assertRaises(RuntimeError):
            mix.KeenDownloader()
        with self.assertRaises(RuntimeError):
            mix.KeenUploader()

    def test_adapter_logging(self):

        ''' Make sure that the internal logging
            interface provided to :py:class:`Adapter`
            implementors works correctly. '''

        _uploader, _downloader = self._valid_adapter(uploader=True, downloader=True, instance=True)

        # make sure logging is logging-like (u/l)
        self.assertTrue(hasattr(_uploader.logging, 'debug'))
        self.assertTrue(hasattr(_uploader.logging, 'info'))
        self.assertTrue(hasattr(_uploader.logging, 'warning'))
        self.assertTrue(hasattr(_uploader.logging, 'error'))
        self.assertTrue(hasattr(_uploader.logging, 'critical'))

        # make sure logging is logging-like (d/l)
        self.assertTrue(hasattr(_downloader.logging, 'debug'))
        self.assertTrue(hasattr(_downloader.logging, 'info'))
        self.assertTrue(hasattr(_downloader.logging, 'warning'))
        self.assertTrue(hasattr(_downloader.logging, 'error'))
        self.assertTrue(hasattr(_downloader.logging, 'critical'))

    def test_adapter_transform(self):

        ''' Make sure that :py:meth:`Adapter.transform`
            works correctly as a soft-abstract method. '''

        _uploader, _downloader = self._valid_adapter(uploader=True, downloader=True, instance=True)

        # make sure transform is there
        self.assertTrue(hasattr(_uploader, 'transform'))
        self.assertTrue(hasattr(_downloader, 'transform'))

        # make sure it returns ``NotImplemented``
        self.assertEqual(_uploader.transform({}), NotImplemented)
        self.assertEqual(_downloader.transform({}), NotImplemented)

        # make sure the abstract method raises ``NotImplementedError``
        with self.assertRaises(NotImplementedError):
            super(mix.Uploader, _uploader).transform({})

        with self.assertRaises(NotImplementedError):
            super(mix.Downloader, _downloader).transform({})


## UploaderTests - tests functionality specific to abstract uploaders.
class UploaderTests(AdapterTests):

    ''' Tests the abstract uploader class, which
        is exposed at :py:class:`mix.Uploader`. '''

    def test_uploader_abc(self):

        ''' Test Abstract Base Class semantics, against
            an invalid and valid :py:class:`mix.Uploader`
            interface. '''

        ## == Invalid Uploader == ##
        with self.assertRaises(TypeError):
            class InvalidUploader(mix.Uploader):
                pass

            InvalidUploader()

        ## == Valid Uploader == ##

        # valid instantiation: with provider
        self._valid_adapter(uploader=True, downloader=False, instance=False)(object())

    def test_uploader_direct(self):

        ''' Test direct use of an :py:class:`Uploader`
            class, which is prohibited. '''

        # invalid instantiation: no provider
        with self.assertRaises(RuntimeError):
            self._valid_adapter(uploader=True, downloader=False, instance=False)()

        # valid instantiation: with provider
        self._valid_adapter(uploader=True, downloader=False, instance=False)(object())

    def test_uploader_preprocess(self):

        ''' Test the :py:meth:`pre_process` method, which
            dispatches :py:meth:`transform` and hands post-
            tranform data back to the adapter for buffering.  '''

        # generate valid adapter to test transform
        ValidUploader = self._valid_adapter(uploader=True, downloader=False, instance=False)
        _valid_uploader = self._valid_adapter(uploader=True, downloader=False, instance=True)

        class ValidTransformUploader(ValidUploader, mix.Uploader):  # must mix-in Uploader to add to enums

            ''' Sample (valid) uploader implementation,
                for testing property access. '''

            def transform(self, data):
                
                ''' Testable, implemented :py:meth:`transform`
                    definition. Used to test non-null transforms. '''

                data['prop'] = not data['prop']  # make sure we can read + write
                data['new_prop'] = 'sup'  # make sure we can add stuff
                return data

        # sample pre-transform data
        data = {'prop': True, 'preserved_prop': 123}

        # try a null-op transform, make sure it defaults to ``NotImplemented``
        result = _valid_uploader.transform(dict(data.items()[:]))

        self.assertEqual(result, NotImplemented)  # should return, NOT raise
        self.assertEqual(data['prop'], True)  # make sure nothing changed
        self.assertEqual(data['preserved_prop'], 123)  # with either of our props

        # shouldn't get any new keys yet
        with self.assertRaises(KeyError):
            data['new_prop']

        # try a valid transform operation
        _transform_uploader = ValidTransformUploader(object())
        transformed_result = _transform_uploader.transform(dict(data.items()[:]))

        self.assertIsInstance(transformed_result, dict)
        self.assertEqual(transformed_result['prop'], (not data['prop']))
        self.assertEqual(transformed_result['new_prop'], 'sup')
        self.assertEqual(transformed_result['preserved_prop'], data['preserved_prop'])

        # make sure the pre-process wrapper works
        noop_transform = _valid_uploader.pre_process(dict(data.items()[:]))

        # noop-transformed data should remain the same
        self.assertEqual(noop_transform['prop'], data['prop'])
        self.assertEqual(noop_transform['preserved_prop'], data['preserved_prop'])

        with self.assertRaises(KeyError):
            noop_transform['new_prop']

        # try a valid pre_process operation
        valid_transform = _transform_uploader.pre_process(dict(data.items()[:]))

        # valid-transform data should come back transformed
        self.assertEqual(valid_transform['prop'], (not data['prop']))
        self.assertEqual(valid_transform['new_prop'], 'sup')
        self.assertEqual(valid_transform['preserved_prop'], data['preserved_prop'])


## DownloaderTests - tests functionality specific to abstract downloaders.
class DownloaderTests(AdapterTests):

    ''' Tests the abstract downloader class, which
        is exposed at :py:class:`mix.Downloader`. '''

    def test_downloader_abc(self):

        ''' Test Abstract Base Class semantics, against
            an invalid and valid :py:class:`mix.Downloader`
            interface. '''

        ## == Invalid Uploader == ##
        with self.assertRaises(TypeError):
            class InvalidDownloader(mix.Downloader):
                pass

            InvalidDownloader()

        ## == Valid Uploader == ##

        # valid instantiation: with provider
        self._valid_adapter(uploader=False, downloader=True, instance=False)(object())

    def test_downloader_direct(self):

        ''' Test direct use of an :py:class:`Uploader`
            class, which is prohibited. '''

        # invalid instantiation: no provider
        with self.assertRaises(RuntimeError):
            self._valid_adapter(uploader=False, downloader=True, instance=False)()

        # valid instantiation: with provider
        self._valid_adapter(uploader=False, downloader=True, instance=False)(object())

    def test_downloader_postprocess(self):

        ''' Test the :py:meth:`post_process` method, which
            dispatches :py:meth:`transform` and hands post-
            tranform data back to the adapter for buffering.  '''

        # generate valid adapter to test transform
        ValidDownloader = self._valid_adapter(uploader=False, downloader=True, instance=False)
        _valid_downloader = self._valid_adapter(uploader=False, downloader=True, instance=True)

        class ValidTransformDownloader(ValidDownloader, mix.Downloader):  # must mix-in Uploader to add to enums

            ''' Sample (valid) downloader implementation,
                for testing property access. '''

            def transform(self, data):
                
                ''' Testable, implemented :py:meth:`transform`
                    definition. Used to test non-null transforms. '''

                data['prop'] = not data['prop']  # make sure we can read + write
                data['new_prop'] = 'sup'  # make sure we can add stuff
                return data

        # sample pre-transform data
        data = {'prop': True, 'preserved_prop': 123}

        # try a null-op transform, make sure it defaults to ``NotImplemented``
        result = _valid_downloader.transform(dict(data.items()[:]))

        self.assertEqual(result, NotImplemented)  # should return, NOT raise
        self.assertEqual(data['prop'], True)  # make sure nothing changed
        self.assertEqual(data['preserved_prop'], 123)  # with either of our props

        # shouldn't get any new keys yet
        with self.assertRaises(KeyError):
            data['new_prop']

        # try a valid transform operation
        _transform_downloader = ValidTransformDownloader(object())
        transformed_result = _transform_downloader.transform(dict(data.items()[:]))

        self.assertIsInstance(transformed_result, dict)
        self.assertEqual(transformed_result['prop'], (not data['prop']))
        self.assertEqual(transformed_result['new_prop'], 'sup')
        self.assertEqual(transformed_result['preserved_prop'], data['preserved_prop'])

        # make sure the pre-process wrapper works
        noop_transform = _valid_downloader.post_process(dict(data.items()[:]))

        # noop-transformed data should remain the same
        self.assertEqual(noop_transform['prop'], data['prop'])
        self.assertEqual(noop_transform['preserved_prop'], data['preserved_prop'])

        with self.assertRaises(KeyError):
            noop_transform['new_prop']

        # try a valid pre_process operation
        valid_transform = _transform_downloader.post_process(dict(data.items()[:]))

        # valid-transform data should come back transformed
        self.assertEqual(valid_transform['prop'], (not data['prop']))
        self.assertEqual(valid_transform['new_prop'], 'sup')
        self.assertEqual(valid_transform['preserved_prop'], data['preserved_prop'])


## FlowTests - tests :py:class:`mix.Importer` data flow.
class FlowTests(test_keen.KeenTests, test_mixpanel.MixpanelTests):

    ''' Tests flow of data and order of method execution
        in :py:class:`Importer` proper. '''

    def _valid_importer(self, instance=False, params=False, _full=False):  # pragma: nocover

        ''' Generate a valid :py:class:`mix.Importer` instance,
            injecting mock parameters as needed. Optionally
            provide a full instance or just the parameters,
            in place of a valid ``Importer`` class. '''

        if not instance and not params:  # pragma: nocover
            return mix.Importer

        if not _full:  # pragma: nocover
            # generate params
            _keen_ = type('KeenMock', (object,), {
                'project_id': None,
                'read_key': None,
                'write_key': None
            })()

            _mixpanel_ = type('MixpanelMock', (object,), {
                'api_key': None,
                'secret_key': None
            })()

            if params and not instance:
                return (_keen_, _mixpanel_), mix.Importer
            return mix.Importer(_keen_, _mixpanel_)

        else:  # pragma: nocover

            # construct valid, mocked providers
            _keen_params, _keen = self._valid_keen_provider(False, True)
            _k_bus, _k_name, _k_library, _k_adapters, _k_config = _keen_params

            _mixpanel_params, _mixpanel = self._valid_mixpanel_provider(False, True)
            _m_bus, _m_name, _m_library, _m_adapters, _m_config = _mixpanel_params

            if params and not instance:
                return (_k_library, _m_library)
            return mix.Importer(_k_library, _m_library)

    def test_importer_construct(self):

        ''' Test direct construction of the
            :py:class:`Importer` object, which is
            the preferred way to dispatch ``importer``
            directly from Python. '''

        _importer_params, Importer = self._valid_importer(params=True)
        _keen, _mixpanel = _importer_params

        # make sure things are not initialized and proper defaults are applied
        self.assertEqual(Importer.cli, False)  # `CLI` mode should default to `False`
        self.assertEqual(Importer.yes, True)  # `yes` mode should default to `False`
        self.assertEqual(Importer.debug, False)  # `debug` mode should default to `False`
        self.assertEqual(Importer.quiet, False)  # `quiet` mode should default to `False`
        self.assertEqual(Importer.log_level, logging.INFO)  # `log_level` should default to `INFO`

        # grab lib ref to mixpanel and remove from visibility
        if 'mixpanel' in sys.modules:
            _mixpanel_mod = sys.modules['mixpanel']
            sys.modules['mixpanel'] = None
        else:
            _mixpanel_mod = None

        # grab lib ref to keen and remove from visibility
        if 'keen' in sys.modules:
            _keen_mod = sys.modules['keen']
            sys.modules['keen'] = None
        else:
            _keen_mod = None

        def _construct_importer(self, keen=None, mixpanel=None, strict=False, _do_check=True):

            ''' Constructor shim for ``Importer`` to help
                with construction testing. '''

            m = Importer(keen, mixpanel, strict=strict)

            if _do_check and m:
                if keen:
                    self.assertTrue('keen' in m)
                else:
                    self.assertFalse('keen' in m)
                if mixpanel:
                    self.assertTrue('mixpanel' in m)
                else:
                    self.assertFalse('mixpanel' in m)

            return m

        ### === STRICT MODE TESTS === ###

        # try strict with no libraries and no global context
        with self.assertRaises(ImportError):
            _construct_importer(self, None, None, True, False)

        # try strict with only keen and no global context
        with self.assertRaises(ImportError):
            _construct_importer(self, _keen, None, True, False)

        # try strict with only mixpanel and no global context
        with self.assertRaises(ImportError):
            _construct_importer(self, None, _mixpanel, True, False)

        # try strict with both libraries and no global context
        _construct_importer(self, _keen, _mixpanel, True, True)

        if _keen_mod:  # we have keen held globally
            
            sys.modules['keen'] = _keen_mod

            # try strict with no libraries and keen in the global context
            with self.assertRaises(ImportError):
                _construct_importer(self, None, None, True, False)

            # try strict with keen only and keen in the global context
            with self.assertRaises(ImportError):
                _construct_importer(self, _keen, None, True, False)

            # try strict with mixpanel only and keen in the global context
            m = _construct_importer(self, None, _mixpanel, True, False)
            self.assertTrue('keen' in m)
            self.assertTrue('mixpanel' in m)

            # try strict with keen and mixpanel and keen in the global context
            m = _construct_importer(self, _keen, _mixpanel, True, False)
            args, provider = m.provider('keen', False, True)
            library, provider, uploader, downloader = args  # extract args

            # perform tests to make sure locally-handed ``keen`` overrides the global copy
            self.assertTrue('keen' in m)
            self.assertTrue('mixpanel' in m)
            self.assertEqual(m.provider('keen', True).lib, _keen)

            # remove keen from global context again
            _keen_mod = sys.modules['keen']
            sys.modules['keen'] = None

        if _mixpanel_mod:

            sys.modules['mixpanel'] = _mixpanel_mod

            # try strict with no libraries and mixpanel in the global context
            with self.assertRaises(ImportError):
                _construct_importer(self, None, None, True, False)

            # try strict with mixpanel only and mixpanel in the global context
            with self.assertRaises(ImportError):
                _construct_importer(self, None, _mixpanel, True, False)

            # try strict with keen only and mixpanel in the global context
            m = _construct_importer(self, _keen, None, True, False)
            self.assertTrue('keen' in m)
            self.assertTrue('mixpanel' in m)

            # try strict with keen and mixpanel and mixpanel in the global context
            m = _construct_importer(self, _keen, _mixpanel, True, False)
            args, provider = m.provider('mixpanel', False, True)
            library, provider, uploader, downloader = args

            # perform tests to make sure locally-handed ``mixpanel`` overrides the global copy
            self.assertTrue('keen' in m)
            self.assertTrue('mixpanel' in m)
            self.assertEqual(library, _mixpanel)

            # remove mixpanel from global context again
            _mixpanel_mod = sys.modules['mixpanel']
            sys.modules['mixpanel'] = None

        if _keen_mod and _mixpanel_mod:

            sys.modules['mixpanel'], sys.modules['keen'] = _mixpanel_mod, _keen_mod

            # try strict with no libraries and both in the global context
            m = _construct_importer(self, None, None, True, False)
            
            # get keen provider stuff
            k_args, k_provider = m.provider('keen', False, True)
            k_lib, k_provider_d, k_up, k_down = k_args

            # get mixpanel provider stuff
            m_args, m_provider = m.provider('mixpanel', False, True)
            m_lib, m_provider_d, m_up, m_down = m_args

            self.assertTrue('keen' in m)
            self.assertTrue('mixpanel' in m)

            # completely clear context and check mount from direct `import`
            sys.modules['mixpanel'], sys.modules['keen'] = None, None
            del sys.modules['mixpanel']
            del sys.modules['keen']

            # try constructing completely from valid global context
            m = _construct_importer(self, None, None, True, False)

            # get keen provider stuff
            k_args, k_provider = m.provider('keen', False, True)
            k_lib, k_provider_d, k_up, k_down = k_args

            # get mixpanel provider stuff
            m_args, m_provider = m.provider('mixpanel', False, True)
            m_lib, m_provider_d, m_up, m_down = m_args

            self.assertTrue('keen' in m)
            self.assertTrue('mixpanel' in m)

    def test_importer_provider(self):

        ''' Make sure that ``Importer`` can hand back
            providers when asked. '''

        _importer = self._valid_importer(instance=True)

        # test regular provider class access
        _keen_klass, _mixpanel_klass = _importer.provider('keen', instance=False), _importer.provider('mixpanel', instance=False)

        # make sure we're handed back classes
        self.assertIsInstance(_keen_klass, type)
        self.assertIsInstance(_mixpanel_klass, type)

        # try to ask for a provider that doesn't exist
        with self.assertRaises(NotImplementedError):
            _importer.provider('blabble', instance=False)

    def test_importer_direct_execution(self):

        ''' Test :py:class:`Importer`'s direct dispatch
            interface, by manually constructing and moving
            through a data flow. Stub out the endpoints/etc
            to allow mock providers. '''

        _importer = self._valid_importer(instance=True, _full=True)

        # prepare args and try an execution flow
        _begin, _end, _args = (
            datetime.datetime(year=2013, month=8, day=20, hour=12, minute=0, second=0),
            datetime.datetime(year=2013, month=8, day=30, hour=12, minute=0, second=0),
            {
                'yes': True,  # skip prompts
                'quiet': False,  # don't silence output
                'verbose': False,  # don't increase output
                'kinds': ['sample_kind'],  # only download sample kind
                'reset_ts': False,  # don't reset timestamps
                'to': 'keen',  # mock a transfer to keen
                'from': 'mixpanel'  # mock a transfer from mixpanel
            }
        )

        # try a flow, because why not
        _importer.execute(_begin, _end, **_args)

    def test_importer_cli_execution(self):

        ''' Simulate a call to :py:class:`Importer` from the
            command line. Make sure that arguments are
            parsed right and the call goes to the right
            ``Importer`` entrypoint (``__call__``). '''

        _importer = self._valid_importer(instance=True, _full=True)

        # prepare args and try an execution flow
        _cliflags = {
            'begin': mix._TO_MIXPANEL_DATE(datetime.datetime(year=2013, month=8, day=20, hour=12, minute=0, second=0)),
            'end': mix._TO_MIXPANEL_DATE(datetime.datetime(year=2013, month=8, day=30, hour=12, minute=0, second=0)),
            'yes': True,  # skip prompts
            'quiet': False,  # don't silence output
            'verbose': False,  # don't increase output
            'kinds': ['sample_kind'],  # only download sample kind
            'reset_ts': False,  # don't reset timestamps
            'to': 'keen',  # mock a transfer to keen
            'from': 'mixpanel'  # mock a transfer from mixpanel
        }

        # try a flow, because why not
        _importer(**_cliflags)


## CLITests - tests :py:class:`mix.Importer` CLI usage.
class CLITests(FlowTests):

    ''' Tests :py:class:`Importer` functionality related to
        command line dispatch and argument parsing. '''

    def _valid_importer_cli(self):

        ''' Simulate a call to :py:class:`Importer` from the
            command line. Make sure that arguments are
            parsed right and the call goes to the right
            ``Importer`` entrypoint (``__call__``). '''

        _importer = self._valid_importer(instance=True, _full=True)

        # prepare args and try an execution flow
        _cliflags = {
            'begin': mix._TO_MIXPANEL_DATE(datetime.datetime(year=2013, month=8, day=20, hour=12, minute=0, second=0)),
            'end': mix._TO_MIXPANEL_DATE(datetime.datetime(year=2013, month=8, day=30, hour=12, minute=0, second=0)),
            'yes': True,  # skip prompts
            'quiet': False,  # don't silence output
            'verbose': False,  # don't increase output
            'kinds': ['sample_kind'],  # only download sample kind
            'reset_ts': False,  # don't reset timestamps
            'to': 'keen',  # mock a transfer to keen
            'from': 'mixpanel'  # mock a transfer from mixpanel
        }

        return _cliflags, _importer

    def test_importer_quiet(self):

        ''' Test the ``-q``/``--quiet`` flags to ``Importer``. '''

        flags, mix = self._valid_importer_cli()

        # run with quiet flag
        flags['quiet'] = True

        # switch stdout with a shim
        original_stdout, sys.stdout = sys.stdout, StringIO.StringIO()

        mix(**flags)

        # switch stdout again
        shim_stdout, sys.stdout = sys.stdout, original_stdout

        self.assertEqual(len(shim_stdout.getvalue()), 188)
        self.assertEqual(shim_stdout.getvalue(), _MINIMAL_OUTPUT)

    def test_importer_verbose(self):

        ''' Test the ``-v``/``--verbose`` flags to ``Importer``. '''

        flags, mix = self._valid_importer_cli()

        # run with quiet flag
        flags['quiet'] = False
        flags['verbose'] = True

        # switch stdout with a shim
        original_stdout, original_stderr, sys.stdout, sys.stderr = sys.stdout, sys.stderr, StringIO.StringIO(), StringIO.StringIO()

        mix(**flags)

        # switch stdout again
        shim_stdout, shim_stderr, sys.stdout, sys.stderr = sys.stdout, sys.stderr, original_stdout, original_stderr

        self.assertTrue(shim_stdout.getvalue() != _MINIMAL_OUTPUT)
        self.assertTrue(len(shim_stdout.getvalue() + shim_stderr.getvalue()) > 182)
