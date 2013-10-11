# -*- coding: utf-8 -*-

'''
    importer
    ~~~~~~~~

    a handy utility for transferring event data
    between ``keen.io`` and ``mixpanel``.

    usage: ``python mixpanel -h``
    (from outside the project directory)

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

__version__ = (1, 1)

# stdlib
import os
import sys
import csv
import abc
import time
import json
import base64
import string
import logging

# timezone data
from tz import timezone
from tz import _TZNAMES
from tz import _TZSHORT
from tz import _TIMEZONES

# datetime tools
from datetime import date
from datetime import tzinfo
from datetime import datetime
from datetime import timedelta


## Globals

# internal constants
_CSV_FILE, _CSV_PARAMS = 'importer-events.csv', {'escapechar': '\\', 'delimiter': ',', 'quoting': csv.QUOTE_NONE}

# keen-related constants
_KEEN_DATE_FMT, _KEEN_DATE_FMT_ISO = '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z'

# mixpanel-related constants
_MIXPANEL_DATE_FMT = '%Y-%m-%d'
_MIXPANEL_API, _MIXPANEL_EXPORT = 'http://mixpanel.com/api', 'https://data.mixpanel.com/api'

# `_TO_TIMESTAMP`: converts a python datetime into a integer timestamp
_TO_TIMESTAMP = lambda dt: int(time.mktime(dt.timetuple()))

# `_PROVIDER`: converts a provider name ("keen") to a sentinel for that provider (`KEEN`)
_PROVIDER = lambda name: getattr(Providers, name.upper())  # return ``KEEN`` for ``keen``
_PROVIDER_IMPL = lambda sentinel: globals()[''.join(sentinel.capitalize())]  # return :py:class:`Keen` for ``KEEN``

# `_PRETTY_DATE`: output a string repr for a date that's easy on the eyes
_PRETTY_DATE = lambda _date: _date.strftime('%a %b %d, %Y')

# `_[TO/FROM]_INTERNAL_DT`: converts between a serialized and in-memory representation of an internal datetime object
_INTERNAL_DATE_FMT = '%Y-%m-%d::%H:%M:%S'
_TO_INTERNAL_DT = lambda dt: dt.astimezone(timezone('UTC')).strftime(_INTERNAL_DATE_FMT)
_FROM_INTERNAL_DT = lambda spec: timezone('UTC').localize(datetime.strptime(spec, _INTERNAL_DATE_FMT))

# `_[TO/FROM]_KEEN_DATE`: converts to/from ISO8601 format and Python `date`
_TO_KEEN_DATE = lambda _date: ''.join((_date.strftime(_KEEN_DATE_FMT_ISO), 'Z' if not _date.tzinfo else ''))
_FROM_KEEN_DATE = lambda spec: timezone('UTC').localize(datetime.strptime('-'.join(spec.replace('Z', '').split('-')[0:3]).split('+')[0], _KEEN_DATE_FMT))

# `_[TO|FROM]_MIXPANEL_DATE`: converts to/from YYYY-MM-DD format and Python `date`
_TO_MIXPANEL_DATE = lambda _date: _date.strftime(_MIXPANEL_DATE_FMT)
_FROM_MIXPANEL_DATE = lambda spec: datetime.strptime(spec, _MIXPANEL_DATE_FMT)

# `PROVIDERS`: global list of installed providers
PROVIDERS = {}


# +=+=+=+ Abstract Classes +=+=+=+ #

class Providers:

    ''' Enumerates available event providers. '''

    pass


class Provider(object):

    ''' Small wrapper object that binds config,
        an :py:class:`Uploader` class and a
        :py:class:`Downloader` class that
        (together) add a provider for ``Importer``. '''

    class __metaclass__(abc.ABCMeta):

        ''' Provider-specific metaclass that registers
            new providers globally. '''

        def __new__(cls, name, bases, properties):

            ''' Construct new provider and register
                with global dict of providers.

                :param name: Class name for construction.
                :param bases: Class bases for construction.
                :param properties: Class-level property map for construction.
                :returns: Constructed :py:class:`Provider` class. '''

            global PROVIDERS

            # construct class (careful of the ABC inheritance tree)
            klass = super(cls, cls).__new__(cls, name, bases, properties)

            # don't register root provider
            if name is 'Provider': return klass

            # register, install & return
            PROVIDERS[name] = klass
            setattr(Providers, name.upper(), name.upper())
            return PROVIDERS[name]

    bus = None  # reference upwards to ``Importer``
    lib = None  # library for this provider
    name = None  # string name of this provider
    client = None  # current client object, from ``lib`` (if applicable)
    config = None  # config from ``config.json``
    adapters = None  # adapter uploader/downloader pair

    def __init__(self, bus, name, library, adapters, **config):

        ''' Initialize this ``Provider``, given
            a provider name and uploader/downloader
            pair.

            :param bus: Reference upwards to the main
            :py:class:`Importer` object.

            :param name: String provider name from
            :py:class:`Provider`, like ``'KEEN'``
            or ``'MIXPANEL'``.

            :param adapters: Tupled pair of a
            :py:class:`Uploader` object and matching
            :py:class:`Downloader` object.

            :param **config: Provider-specific config
            values found in ``config.json``.

            :returns: Nothing, as this method is a
            constructor. '''

        self.bus, self.name, self.lib, self.config, self.adapters = (
            bus,
            name,
            library,
            config,
            adapters
        )

        if not isinstance(adapters, tuple) or len(adapters) < 2:
            raise TypeError('Must provide a valid `Downloader` and `Uploader`'
                            ' tupled pair to the `Provider` constructor. Got: `%s`.' % adapters)

        self.initialize()  # dispatch provider-level initialize

    @property
    def uploader(self):

        ''' Grab and initialize this ``Provider``'s
            local :py:class:`Uploader`, if there isn't
            one already instantiated.

            :returns: An instantiated and configured
            :py:class:`Uploader`, for this ``Provider``. '''

        uploader, downloader = self.adapters
        if isinstance(uploader, type):  # does it need initializing?
            adapter = uploader(self)
            self.adapters = (adapter, downloader)
            return adapter
        return uploader  # already instantiated

    @property
    def downloader(self):

        ''' Grab and initialize this ``Provider``'s
            local :py:class:`Downloader`, if there isn't
            one already instantiated.

            :returns: An instantiated and configured
            :py:class:`Downloader`, for this ``Provider``. '''

        uploader, downloader = self.adapters
        if isinstance(downloader, type):  # does it need initializing?
            adapter = downloader(self)
            self.adapters = (uploader, adapter)
            return adapter
        return downloader  # already instantiated

    @property
    def logging(self):

        ''' Build a child logger to the root ``importer``
            logger that is specific to this ``Provider``.

            :returns: Customized :py:mod:`logging.Logger`
            object. '''

        if self.bus and hasattr(self.bus, 'logging'):  # pragma: nocover
            return self.bus.logging.getChild(self.name.capitalize())
        return logging

    def __repr__(self):

        ''' Generate a nice string representation
            of this provider.

            :returns: A string like ``'Provider(KEEN)'``. '''

        return 'Provider(%s)' % self.name

    @abc.abstractmethod
    def initialize(self):  # pragma: nocover

        ''' Initialization hook for :py:class:`Provider`
            implementors. Dispatched by :py:meth:`__init__`
            upon provider construction.

            :raises NotImplementedError: If the root abstract
            method is called directly on the ABC-enforced
            class.

            :returns: Nothing, as this is a constructor-like
            method. '''

        raise NotImplementedError('`Provider.initialize` is abstract'
                                  ' and cannot be dispatched directly.')


class Adapter(object):

    ''' Abstract class that specifies basic
        methods that both :py:class:`Uploader`
        and :py:class:`Downloader` share. '''

    utc = timezone('UTC')

    # == Encapsulated ABC Enforcer == #
    class __metaclass__(abc.ABCMeta):

        ''' Encapsulated adapter metaclass that
            enforces ABC semantics and prevents
            :py:class:`Adapter` children that are
            not :py:class:`Uploader` or
            :py:class:`Downloader`. '''

        def __new__(cls, name, bases, prop_map):

            ''' Factory a new :py:class:`Adapter` class,
                by yielding to :py:mod:`abc` if it is
                approved for implementation. '''

            prop_map['__name__'] = name  # set name
            prop_map['__bases__'] = bases  # set bases

            # allow this class (obviously)
            if (name == 'Adapter' and bases == (object,)):

                # overwrite class name to hide metaclass magic
                cls.__name__ = name

                # yield to ABCMeta, but run in this class' context
                return type.__new__(cls, name, bases, prop_map)

            # disallow non (downloaders || uploaders)
            if name in frozenset(('Uploader', 'Downloader')):
                if len(bases) == 1 and bases[0] is Adapter:
                    # it's a valid adapter
                    return super(Adapter.__metaclass__, cls).__new__(cls, name, bases, prop_map)

            # implementors of `Uploader` and `Downloader` are obviously allowed
            if Uploader in bases or Downloader in bases:
                return super(Adapter.__metaclass__, cls).__new__(cls, name, bases, prop_map)

            # only :py:class:`Uploader` and :py:class:`Downloader` can implement :py:class:`Adapter`
            raise RuntimeError('`Adapter` does not support implementations other than'
                               ' `Downloader` and `Uploader`. If you would like to extend'
                               ' `importer`, you should implement a `Provider` with an'
                               ' `Uploader`/`Downloader` pair. See docs for more info.')


    # == Class Members == #
    provider = None  # bridge up to this adapter's provider

    def __new__(cls, *args, **kwargs):

        ''' Enforce that abstract :py:class:`Adapter`
            implementors cannot be instantiated directly,
            as they are abstract and define no real
            functionality.

            This method passes everything on to
            :py:meth:`__init__`, assuming the class being
            constructed passes our tests.

            :param args: Positional construction arguments.
            :param kwargs: Keyword-based construction arguments. '''

        if cls.__name__ in frozenset(('Adapter', 'Uploader', 'Downloader')):
            raise TypeError('Cannot instantiate `%s` directly, as it is abstract.' % cls.__name__)
        return super(Adapter, cls).__new__(cls, *args, **kwargs)

    def __init__(self, provider=None):

        ''' Initialize this :py:class:`Adapter`.
            Takes a Python library to attach locally
            and a set of config handed in from the
            local :file:`config.json`.

            :param provider: Parent :py:class:`Provider`
            encapsulating this ``Adapter``. Allows access
            to ``Provider``-specific config and a ref
            to this ``Adapter``'s library.

            :returns: Nothing, as this method is a
            constructor. '''

        # must be instantiated from a provider, not directly
        if not provider:
            raise RuntimeError('Cannot instantiate an `Adapter` or direct subclass'
                               ' directly. `Adapter` classes must be used from a'
                               ' valid `Provider`.')

        # set provider and propagate to `self.initialize`, if present
        self.provider = provider
        if hasattr(self, 'initialize'):  # pragma: nocover
            self.initialize()

    @property
    def logging(self):

        ''' Build a child logger to the root ``importer``
            logger that is specific to this ``Provider``.

            :returns: Customized :py:mod:`logging.Logger`
            object. '''

        if self.provider and hasattr(self.provider, 'logging') and not isinstance(self.provider.logging, type(os)):  # pragma: nocover
            # return child logger to provider, like `Uploader` so it ends up as `keen.Uploader`
            return self.provider.logging.getChild(self.__class__.__name__.replace(self.provider.__class__.__name__, ''))
        return logging

    @abc.abstractmethod
    def transform(self, data):  # pragma: nocover

        ''' Hook for :py:class:`Adapter` implementors that
            allows transformations to be applied to data
            moving up (in the case of an :py:class:`Uploader`)
            or down (in the case of a :py:class:`Downloader`).

            The :py:meth:`transform` method is called once per event
            moving through the :py:class:`Adapter`. Think of it as a
            ``map()``-type hook, as the return value is taken **in place**
            of the original data.

            If the adapter means not to implement :py:meth:`transform`,
            it can return the special value ``NotImplemented``, which
            indicates that transformation is not required. If
            ``NotImplemented`` is not the return value, the result is
            taken as the transformed data.

            :param data: Raw data to transform.

            :raises: ``NotImplementedError``, if the root abstract
            method is called, via ``super()`` or directly.

            :returns: Transformed data, or ``NotImplemented``, if
            this class does not implement transformations. '''

        raise NotImplementedError('`Provider.transform` is abstract'
                                  ' and cannot be dispatched directly.')


class Uploader(Adapter):

    ''' Abstract class for an Uploader object,
        which manages the process of uploading
        events to a particular service. '''

    def pre_process(self, data):

        ''' Pre-process hook that implements the transform
            flow for data staged for upload. Called once
            for each event that is due to be uploaded.

            :param data: Raw data that would be uploaded, usually
            from the buffered CSV file of downloaded data.

            :raises: Nothing.

            :returns: Transformed data, from :py:meth:`transform`,
            or the unmodified data if no transform was supported/
            accepted. '''

        transformed = self.transform(data)
        return transformed if transformed is not NotImplemented else data

    @abc.abstractmethod
    def upload(self, kind, data, timestamp=None):  # pragma: nocover

        ''' Abstract method specifying the existence
            (and interface) to ``upload`` some event
            data. Must be overridden by a subclass.

            :param kind: Event kind name to upload.

            :param data: Event data to upload.

            :param timestamp: Timestamp for the new
            event. ``datetime.now()`` is taken if
            ``None`` is passed.

            :raises NotImplementedError: Always, as
            this method is abstract. '''

        raise NotImplementedError()

    @abc.abstractmethod
    def commit(self):  # pragma: nocover

        ''' Event commit hook, called at the end of the
            upload flow to indicate the stream of events
            has been exhausted and is ready to send.

            :py:class:`Uploader` implementors must define
            this method.

            :returns: The count of buffered events that
            are due to be uploaded, as an ``int``.'''

        raise NotImplementedError()

    def transform(self, data):

        ''' Data transformation hook. Left unimplemented
            by default.

            :param data: Pre-transform data to perform
            our work on.

            :raises: Nothing.

            :returns: ``NotImplemented``, a special value
            specifying that this method is unimplemented
            by default. '''

        return NotImplemented


class Downloader(Adapter):

    ''' Abstract class for a Downloader object.
        Responsible for managing the process of
        downloading events from a particular
        service. '''

    def post_process(self, data):

        ''' Post-process data that has just been downloaded,
            to cleanse/tune the data for compatibility or
            better value to ``Importer``.

            :param data: Raw data that has recently been
            downloaded and is awaiting transformation.

            :raises: Nothing.

            :returns: Transformed data, from :py:meth:`transform`,
            or the unmodified data if no transform was supported/
            accepted. '''

        transformed = self.transform(data)
        return transformed if transformed is not NotImplemented else data

    @abc.abstractmethod
    def download(self, begin, end, kinds):  # pragma: nocover

        ''' Abstract method specifying the existence
            (and interface) to ``download`` some event
            data. Must be overridden by a subclass.

            :param begin: Begin date for event data
            to download.

            :param end: End date for event data to
            download.

            :param kinds: Event kind names to
            download.

            :raises NotImplementedError: Always, as
            this method is abstract. '''

        raise NotImplementedError()

    def transform(self, data):

        ''' Data transformation hook. Left unimplemented
            by default.

            :param data: Pre-transform data to perform
            our work on.

            :raises: Nothing.

            :returns: ``NotImplemented``, a special value
            specifying that this method is unimplemented
            by default. '''

        return NotImplemented


# +=+=+=+ Keen Classes +=+=+=+ #

class Keen(Provider):

    ''' Handles operations specific to ``Keen``. '''

    def initialize(self):

        ''' Initialize this ``Keen`` provider
            instance.

            :returns: Nothing, as this method
            is a delegated constructor. '''

        self.lib.project_id, self.lib.write_key, self.lib.read_key = (
            self.config.get('project_id'),
            self.config.get('write_key'),
            self.config.get('read_key')
        )

        if self.config.get('endpoint'):  # custom endpoint?
            self.lib.api.KeenApi.base_url = self.config.get('endpoint')

    def _set_config(self, name, value):

        ''' Set an internal config value, such
            as ``project_id`` or ``write_key``/
            ``read_key``.

            Just proxies access to module-level
            globals in ``Keen``, or wherever
            config exists for ``Keen``.

            :param name: Name of the config value
            to set.

            :param value: Value to set the config
            entry to.

            :raises AttributeError: If the config
            key is not in the list of valid config
            items, which is ``project_id``,
            ``write_key`` and ``read_key``.

            :returns: ``self``, for chainability. '''

        # only set globals that are allowed
        if name not in frozenset(('project_id', 'read_key', 'write_key')):
            raise ValueError('Cannot set unknown Keen config value: `%s`.' % name)

        # it's valid, set it and return `self`
        self.config[name] = value
        setattr(self.lib, name, value)
        return self

    # `_[get/set]_read_key`: small get/set methods to manage a read key
    _get_read_key, _set_read_key = (lambda self: self.lib.read_key), (lambda self, value: self._set_config('read_key', value))

    # `_[get/set]_write_key`: small get/set methods to manage a write key
    _get_write_key, _set_write_key = (lambda self: self.lib.write_key), (lambda self, value: self._set_config('write_key', value))

    # `_[get/set]_project_id`: small get/set methods to manage a project ID
    _get_project_id, _set_project_id = (lambda self: self.lib.project_id), (lambda self, value: self._set_config('project_id', value))

    # `read_key/write_key/project_id`: get/set proxies for config values
    read_key, write_key, project_id = property(_get_read_key, _set_read_key), property(_get_write_key, _set_write_key), property(_get_project_id, _set_project_id)


class KeenUploader(Uploader):

    ''' Uploads CSV-based event data to Keen.
        Implements :py:class:`Uploader`. '''

    events_by_kind = {}
    timezone = timezone('UTC')

    def upload(self, kind, data, timestamp=None):

        ''' Upload some event data to ``Keen``.
            Implements the abstract method
            :py:meth:`Uploader.upload`.

            :param kind: Kind name of event to
            upload to ``Keen``.

            :param data: Data for event to upload
            to ``Keen``.

            :param timestamp: Timestamp to set for
            new event. ``datetime.now()`` is taken
            if ``None`` is passed.

            :returns: Result of the low-level Keen
            ``add_event`` call. '''

        if timestamp and not isinstance(timestamp, datetime):
            raise RuntimeError('Timestamps passed to `upload` must be `None` or a Python datetime.')

        # provision kind bucket if it's not there
        if kind not in self.events_by_kind:
            self.events_by_kind[kind] = []

        # decode event JSON
        deserialized = dict(((k.replace('$', ''), v) for k, v in json.loads(data).iteritems()))

        # assign timestamp, if available #@TODO(sgammon): fix timestamps
        try:
            if 'keen' not in deserialized:
                if timestamp:
                    if not timestamp.tzinfo:
                        # timestamp should come in as UTC, make sure it is
                        self.timezone.localize(timestamp)
                else:
                    timestamp = self.timezone.localize(datetime.now())

                deserialized['keen'] = {'timestamp': _TO_KEEN_DATE(timestamp)}

        except TypeError:
            self.logging.critical('Failed to decode timestamp for event!')

        # buffer and return
        return self.events_by_kind[kind].append(deserialized)

    def commit(self):

        ''' Flush the local event buffer to Keen.

            :returns: Result of the low-level Keen call. '''

        # add events via client
        count, result = (
            sum(map(len, self.events_by_kind.itervalues())),  # grab summed length of all buffered events
            self.provider.lib.add_events(self.events_by_kind)  # add the events to Keen (this results in a web request)
        )

        # return count of events we sent
        return count


class KeenDownloader(Downloader):

    ''' Downloads event data from Keen into CSV.
        Implements :py:class:`Downloader`. '''

    def download(self, begin, end, kinds):

        ''' Download some event data from ``Keen``.
            Implements the abstract method
            :py:meth:`Downloader.download`.

            :param begin: Begin date for events to
            download from ``Keen``. Accepts a Python
            :py:class:`datetime.datetime`.

            :param end: End date for events to
            download from ``Keen``. Accepts a Python
            :py:class:`datetime.datetime`.

            :param kinds: Event kind names to
            to download from ``Keen``. Accepts any
            nonduplicate iterable set of ``basestring``s.

            :raises NotImplementedError: Always, as
            this method is currently not implemented.

            :returns: ``yields`` the event ``kind``,
            the ``deserialized`` event, and the event's
            decoded ``timestamp``, in that order, packed
            into a tuple. '''

        _buffered_kinds = []
        for kind in kinds:

            # `extract` for kind, deserialize and yield
            for deserialized in self.provider.lib.extraction(kind, {'start': _TO_KEEN_DATE(begin), 'end': _TO_KEEN_DATE(end)}):

                # pull out timestamp and yield
                yield (kind, deserialized, _FROM_KEEN_DATE(deserialized.get('keen', {}).get('timestamp')))  # this will come out as UTC already (yay!)


# +=+=+=+ Mixpanel Classes +=+=+=+ #

class Mixpanel(Provider):

    ''' Handles operations specific to ``Mixpanel``. '''

    gmt = timezone('GMT')  # static ``GMT`` timezone because why not
    timezone = None  # account timezone :py:class:`tzinfo` descendant

    def initialize(self):

        ''' Initialize this ``Mixpanel`` provider
            instance.

            :returns: Nothing, as this method
            is a delegated constructor. '''

        # resolve timezone info and factory class
        self.timezone = timezone(self.config.get('timezone', 'UTC'))

        # setup API client with keys and proper endpoint
        self.client = self.lib.Mixpanel(self.config.get('api_key'), self.config.get('api_secret'))
        self.client.ENDPOINT = _MIXPANEL_API

    def __toggle_export__(self, type=None, value=None, traceback=None):

        ''' Enter or exit "Export Mode," which switches
            the Mixpanel API endpoint, since it is
            different for the Export API.

            :param type:
            :param value:
            :param traceback:

            :returns: ``self``, for method
            chainability. '''

        # resolve new endpoint and toggle
        self.client.ENDPOINT = _MIXPANEL_EXPORT if (self.client.ENDPOINT == _MIXPANEL_API) else _MIXPANEL_API
        self.logging.debug('Switched Mixpanel endpoint to "%s".' % self.client.ENDPOINT)

        if traceback: raise  # always re-raise exceptions (we can't stop, this is bat country)
        
        return self

    # `__enter__`/`__exit__`: co-opt Python's `with` for endpoint switching
    __enter__ = __exit__ = lambda self, *args: self.__toggle_export__(*args)


class MixpanelUploader(Uploader):

    ''' Uploads CSV-based event data to Mixpanel.
        Implements :py:class:`Uploader`. '''

    events_by_kind = {}

    def upload(self, kind, data, timestamp=None):

        ''' Upload some event data to ``Mixpanel``.
            Implements the abstract method
            :py:meth:`Uploader.upload`.

            :param kind: Kind name of the event
            to upload to ``Mixpanel``.

            :param data: Data for the event to
            upload to ``Mixpanel``.

            :param timestamp: Timestamp to set
            for the new event. ``datetime.now()``
            is taken if ``None`` is passed.

            :raises NotImplementedError:
            :returns: '''

        # allocate kind buffer, if it's not there already
        if kind not in self.events_by_kind:
            self.events_by_kind[kind] = []

        # deserialize event from JSON, replacing dollar signs in keys as we go
        deserialized = dict(((k.replace('$', ''), v) for k, v in json.loads(data).iteritems()))

        if 'time' in deserialized:
            deserialized['original_time'] = deserialized['time']
            deserialized['time'] = int(time.mktime(timestamp.astimezone(self.provider.gmt).timetuple()))

        #@TODO(sgammon): MUST CONVERT TO GMT. WHY????????? WTF JUST WHY

        # buffer event with the rest of its kind
        return self.events_by_kind[kind].append(deserialized)

    def commit(self):

        ''' Commit buffered events to ``Mixpanel``.
            Takes buffered events from
            :py:attr:`events_by_kind` and uploads
            in batches.

            :returns: Total count of events uploaded
            to ``Mixpanel``, across all batches. '''

        # count buffered events
        count = sum(map(len, self.events_by_kind.itervalues()))

        for kind in self.events_by_kind:

            for event in self.events_by_kind[kind]:

                # kick off uploader job
                result = self.provider.client.request(['import'], {
                    'ip': 0,  # we're not the event source, just a relay
                    'data': base64.b64encode(json.dumps(event))
                })

        return count


class MixpanelDownloader(Downloader):

    ''' Downloads event data from Mixpanel into CSV.
        Implements :py:class:`Downloader`. '''

    def download(self, begin, end, kinds):

        ''' Download some event data from ``Mixpanel``.
            Implements the abstract method
            :py:meth:`Downloader.download`.

            :param begin: Begin date for event range
            to download from ``Mixpanel``.

            :param end: End date for event range to
            download from ``Mixpanel``.

            :param kinds: List of kind names for event
            types to download.

            :raises RuntimeError: Re-raises internal
            ``Mixpanel`` exceptions as ``RuntimeError``.

            :returns: Yields each event as it is received,
            in the format ``tuple(kind, data, timestamp)``.
            The ``timestamp`` tuple element is a Python
            ``datetime``, localized to the Mixpanel account's
            timezone (set in ``config.json`` at
            ``mixpanel['timezone'])``, and converted to ``UTC``. '''

        with self.provider as mixpanel:  # enter `export` mode, which switches endpoints

            # export events for each kind in the date range
            result = mixpanel.client.request(['export'], {
                'from_date': _TO_MIXPANEL_DATE(begin),
                'to_date': _TO_MIXPANEL_DATE(end),
                'event': kinds
            })

            # check for mixpanel API errors
            if 'error' in result:  # pragma: nocover

                # @TODO(sgammon): proper mixpanel error handling
                if self.provider.bus.debug:
                    import pdb; pdb.set_trace()

                raise RuntimeError(' '.join(('Mixpanel:', result['error'])))

            else:  # no error ocurred: parse newline-separated JSON events
                event_count, error_count, ignore_errors = 0, 0, False
                for event in filter(lambda x: x, result.split("\n")):  # (subtly filter out falsy empty strings)
                    
                    event_count += 1
                    self.logging.debug('Got raw event: "%s".' % event)

                    try:

                        # try to deserialize
                        deserialized = json.loads(event)

                    except Exception as e:  # pragma: nocover

                        self.logging.debug('Encountered JSON exception: "%s".' % str(e))
                        self.logging.error('Failed to decode JSON from blob.')

                        # prompt for what to do from here
                        if (not ignore_errors) and self.provider.bus.prompt("\n\n`Importer` encountered an issue decoding the following blob:\n%s\n" % event, "Ignore errors?"):
                            ignore_errors = True

                        # fail if we've tried more than 5 times and every time has failed
                        error_count += 1
                        if (event_count > 5) and error_count == event_count:
                            raise RuntimeError(' '.join(('Mixpanel:', 'too many errors.')))

                    else:

                        # convert to python datetime
                        ts = deserialized['properties']['time']
                        if isinstance(ts, int):
                            ts = datetime.fromtimestamp(ts)

                        # yield event to caller
                        yield (deserialized['event'], deserialized['properties'], self.provider.timezone.localize(ts).astimezone(self.utc))


# +=+=+=+ Importer +=+=+=+ #

class Importer(object):

    ''' Logic to stitch :py:class:`Uploader` and
        :py:class:`Downloader` classes together
        into a handy CLI tool. '''

    # == Public Members == #
    cli = False  # are we running via CLI?
    yes = True  # assume `yes` to all prompts
    debug = False  # whether debug mode is active
    quiet = False  # whether quiet mode is active
    argset = None  # arguments passed to us via command line
    log_level = logging.INFO  # default logging level
    log_format = "%(levelname)s [importer]: %(message)s"  # format string for logs

    # == Private Members == #
    __logger = None  # dedicated logger
    __buffer = None  # buffer used for writing / reading events
    __config = None  # interpreted config object (`config.json`)
    __providers = None  # references to current provider adapters

    def __init__(self, keen=None, mixpanel=None, strict=False):

        ''' Initialize this :py:class:`Importer` run.
            Take dependent libraries injected via
            parameters to this method and prepare to
            run the tool.

            :param keen: ``Keen`` API client library to
            use for ``Keen`` operations. If ``None`` is
            provided, ``Importer`` attemps to load ``Keen``
            itself with a regular import.

            :param mixpanel: ``Mixpanel`` API client
            library to use for ``Mixpanel`` operations.
            If ``None`` is provided, ``Importer`` attempts
            to load ``Mixpanel`` itself with a regular
            import.

            :param strict: Fail if we aren't provided with
            ``keen``/``mixpanel`` libraries, and they are
            not immediately importable at expected default
            paths.

            :raises ImportError: Re-raises encountered library
            import issues, if libraries are not provided via
            the regular constructor params.

            :returns: Nothing, as this method is
            a constructor. '''

        self.__local_logging__ = not (not keen and not mixpanel)  # direct instantiation probably, turn off local logging

        # if we're not handed libraries, fix `sys.path` because we're probably being imported
        if not keen and not mixpanel:  # @TODO(sgammon): why did I ever do this?
            self.fix_path()

        if not keen:

            try:

                if 'keen' not in sys.modules:
                    import keen
                else:  # if it's an explicit `None` it's coming from the test framework, fail it
                    if sys.modules['keen'] is None:
                        raise ImportError('Failed to resolve library `Keen`.')
                    keen = sys.modules['keen']

            except ImportError:

                self.logging.critical('Failed to resolve `Keen` library. Integration with Keen may not work.')
                if strict:
                    self.logging.critical('Strict mode is active. Failing because we can\'t find `keen`.')
                    raise

        if not mixpanel:

            try:

                if 'mixpanel' not in sys.modules:
                    import mixpanel
                else:  # if it's an explicit `None` it's coming from the test framework, fail it
                    if sys.modules['mixpanel'] is None:
                        raise ImportError('Failed to resolve library `Mixpanel`.')
                    mixpanel = sys.modules['mixpanel']

            except ImportError:

                self.logging.critical('Failed to resolve `Mixpanel` library. Integration with Mixpanel may not work.')
                if strict:
                    self.logging.critical('Strict mode is active. Failing because we can\'t find `mixpanel`.')
                    raise

        # bind libraries locally
        self.__providers = {
            Providers.KEEN: (keen, Keen, KeenUploader, KeenDownloader) if keen else None,
            Providers.MIXPANEL: (mixpanel, Mixpanel, MixpanelUploader, MixpanelDownloader) if mixpanel else None
        }

    @property
    def config(self):

        ''' Return loaded configuration for the current
            :py:class:`Importer` run. This may involve
            parsing the :file:`config.json` if it hasn't
            been already.

            :returns: Interpreted config blob from
            ``config.json`` file, or ``{'debug': True}``. '''

        if not self.__config:

            # resolve configuration path
            if self.argset and hasattr(self.argset, 'config_file') and self.argset.config_file:
                config_path = self.argset.config_file
            else:
                config_path = os.path.join(os.path.dirname(__file__), 'config.json')

            # try loading config
            try:
                self.logging.debug("Loading 'config.json'...")
                with open(config_path, 'r') as config_handle:
                    self.__config = json.loads(config_handle.read())

            except (IOError, OSError, ValueError, TypeError) as e:  # pragma: nocover

                # raise warning and continue
                self.__config = {'importer': {}, 'keen': {}, 'mixpanel': {}, 'debug': True}
                self.logging.warning('Failed to parse `config.json` file. Falling back to default config. '
                                     'Got exception: "%s".' % str(e))

        return self.__config

    # `mixconfig`: shortcut to grab `importer` config
    mixconfig = property(lambda self: self.config.get('importer', {'debug': True}))

    @property
    def logging(self):

        ''' Local proxy to Python logging for the
            :py:class:`Importer` tool.

            :returns: Configured :py:mod:`logging`
            channel. '''

        if self.__local_logging__:
            if not self.__logger:
                self.__logger = logging.getLogger().getChild('importer')
            return self.__logger  # @TODO(sgammon): file-based logging
        return logging

    @staticmethod
    def fix_path():

        ''' Fix the system path, if we're running
            :py:class:`Importer` directly instead
            of via the CLI, which fixes the path
            for us.

            :returns: :py:attr:`sys.path`, because
            why not. '''

        prdir = os.path.dirname(__file__)  # get project directory and lib directory
        libdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib')

        for i in (prdir, libdir):
            if i not in sys.path:
                sys.path.insert(0, i)

    def say(self, message):  # pragma: nocover

        ''' Quick shortcut for info-type messages
            that are procedural and not meant for
            logging.

            :param message: String message to print.
            :returns: ``self``, for chainability. '''

        print '[importer]: %s' % message
        return self

    def prompt(self, text, prompt='Continue?'):  # pragma: nocover

        ''' Prompt the user if we should continue
            operating. If ``yes`` mode is on, skip
            the prompt and assume a truthy value.

            :param text: String to output to the
            user before prompting.

            :param prompt: Question to prompt the
            user with after printing ``text``.
            Defaults to "Continue?".

            :returns: Bool indicating whether the
            user said we should continue, or
            ``True`` in every case if ``self.yes``
            is activated. '''

        if text and not self.quiet: print text
        return self.yes or (
            raw_input('%s [y/n]: ' % prompt) in ('y', 'yes', 'yup', 'mmk', 'go ahead', '1')
        )

    def provider(self, code, instance=True, _all=False):

        ''' Provide a small wrapper and prepared
            :py:class:`Uploader`/:py:class:`Downloader`
            pair for a certain provider.

            :param code: Provider code, mapped at
            :py:class:`Provider`.

            :param instance: Bool flag indicating whether
            a full instance is requested, or we just need
            the ``provider``'s class/construction params.

            :param _all: Bool flag indicating whether the
            construction params that *would be* or *were*
            used (depending on ``instance``) be returned
            in the response, as the first item in a two-
            item ``tuple``.

            :raises NotImplementedError: If the requested
            provider ``code`` cannot be resolved to a valid
            provider. Checking provider support is easy -
            simply use the ``in`` operator with the provider
            name and the ``Importer`` object itself: ``'keen' in Importer``.

            :raises RuntimeError: Re-raises exceptions
            that occur during construction of the
            :py:class:`Provider` object.

            :returns: Instance of :py:class:`Provider`,
            prepared with a :py:class:`Uploader` and
            :py:class:`Downloader` and all relevant
            config. '''

        try:
            # covert to provider code
            code = _PROVIDER(code)

        except AttributeError:  # nothing we've ever heard of before
            raise NotImplementedError('Requested provider `%s` is not supported.' % code)

        if code not in self:  # pragma: nocover
            raise NotImplementedError('Requested provider `%s` is not supported '
                                      'or not implemented.' % code)

        # grab library and up/down classes
        self.logging.info('Loading provider: "%s".' % code)
        library, provider, uploader, downloader = self.__providers[code]

        if instance:
            p = provider(
                self,
                code,
                library,
                (uploader, downloader),
                **self.config.get(code.lower(), {'debug': True})
            )
            return p
        if _all:
            return (library, provider, uploader, downloader), provider
        return provider

    def __contains__(self, provider):

        ''' Check ``Importer`` for support for the given
            provider name, which is resolved through
            :py:func:`_PROVIDER` and checked for support.

            Following the ``__contains__`` protocol, ``True``
            is returned if ``provider`` is supported, else
            ``False``.

            :param provider: Name (``str``) of the provider
            we wish to check support for. '''

        return _PROVIDER(provider) in self.__providers

    def execute(self, begin, end, **arguments):

        ''' Execute :py:class:`Importer`, performing
            the requested operations as interpreted
            via :file:`config.json` and the provided
            command-line arguments.

            :param begin: Python py:class:`datetime.date`
            object representing the start of the range
            of events to transfer.

            :param end: Python py:class:`datetime.date`
            object representing the end of the range
            of events to transfer.

            :param **arguments: Args for ``importer``,
            usually passed in via the command line.
            Takes the same keyword arguments as the
            CLI interface.

            :returns: Bool indicating whether this
            ``Importer`` operation was successful.
            ``True`` indicates success. '''

        self.logging.debug('Got arguments: %s' % str(arguments))
        self.logging.debug('Got range: BEGIN(%s), END(%s)' % (begin.isoformat(), end.isoformat()))

        self.yes, self.debug, self.quiet, self.verbose = (
            arguments.get('yes', False),
            arguments.get('debug', False),
            arguments.get('quiet', False),
            arguments.get('verbose', False)
        )

        # grab kinds, to/from providers
        kinds, source, target, reset_ts = [arguments[x] for x in ('kinds', 'from', 'to', 'reset_ts')]
        
        # resolve provider object
        source, target = self.provider(source), self.provider(target)
        self.logging.debug('Providers: SOURCE(%s) -> TARGET(%s)' % (source, target))

        # unless we were told to 'yes' all prompts, confirm what we're doing
        if not self.yes and not self.prompt("""

    Importer plans to:
        -- Transfer event data from %s to %s
        -- That occurred between %s and %s
        -- %s existing timestamps
        -- For the following event types: %s

    """ % (

            source.name.capitalize(),
            target.name.capitalize(),
            _PRETTY_DATE(begin),
            _PRETTY_DATE(end),
            'Reset' if reset_ts else 'Preserve',
            "\n" + "\n".join(map(lambda x: "\t\t-- %s" % x, kinds))

        )):  # pragma: nocover

            return True  # exit without error

        # calculate buffer file path
        download_buffer_path = os.path.join(os.path.dirname(__file__), _CSV_FILE)
        self.logging.debug('Buffering downloaded data to "%s"...' % download_buffer_path)

        # open CSV and set up download buffer file
        event_count = 0
        with open(download_buffer_path, 'wb') as download_buffer:

            # get CSV writer
            writer = csv.writer(download_buffer, **_CSV_PARAMS)

            # fetch source events
            self.say('Beginning event data download...')
            for kind, data, timestamp in source.downloader.download(begin, end, kinds):

                event_count += 1

                # log about it
                self.logging.info('Downloaded "%s" (event #%s @ %s bytes)...' % (kind, event_count, sys.getsizeof(data)))
                self.logging.debug('Got event data: "%s".' % (str(data)))

                # write to our buffer file
                writer.writerow((kind, _TO_INTERNAL_DT(timestamp), json.dumps(source.downloader.post_process(data))))

            self.logging.info('Download complete.')

        if self.cli:
            time.sleep(2)  # give the user a chance to catch up

        if event_count is 0:  # pragma: nocover
            self.say('Total events collected: 0.')
            self.say('No events to transfer. Exiting.')
            return True

        _msg_context = (str(event_count), source.name.capitalize(), target.name.capitalize())
        if (not self.yes) and not self.prompt("\n\nCollected %s events from %s.\nReady to upload to %s.\n" % _msg_context):  # pragma: nocover
            self.logging.info('Exiting on user cancel.')
            return True

        # open CSV in read mode and start upload
        event_count = 0
        with open(download_buffer_path, 'rb') as upload_buffer:

            # for each event, upload to target
            self.say('Beginning event data upload...')
            for event in csv.reader(upload_buffer, **_CSV_PARAMS):

                event_count += 1

                # extract info
                kind, timestamp, data = event

                self.logging.info('Uploading "%s" (event #%s)...' % (kind, event_count))
                self.logging.debug('Uploading event data: "%s".' % event)

                target.uploader.upload(kind, target.uploader.pre_process(data), _FROM_INTERNAL_DT(timestamp) if not reset_ts else None)  # extract row data and upload

            # dispatch commit(), if available
            try:
                self.say('Committing events...')
                target.uploader.commit()
            except NotImplementedError:  # pragma: nocover
                self.logging.critical('Failed to commit events.')

            self.say('Upload complete.')
            self.logging.info('Transferred %s events to %s.' % (str(event_count), target.name.capitalize()))

        if self.cli:
            time.sleep(2)  # give the user a chance to catch up

        if self.yes or self.prompt("\n\n`Importer` has finished transferring %s events\n "
                           "from %s to %s. The transferred data is currently\n "
                           "buffered in a file called '%s' - would you like to\n "
                           "keep it as a backup?" % (event_count, source.name.capitalize(), target.name.capitalize(), _CSV_FILE), "Keep file?"):

            try:
                os.remove(download_buffer_path)  # delete the buffer file if requested
            except:  # pragma: nocover
                self.logging.error('Failed to remove buffer file at path "%s". This is probably due to permissions.' % download_buffer_path)

        self.logging.debug('Finished work.')
        self.say('Done, exiting `Importer`.')
        return True  # exit without error

    def __call__(self, **cli):

        ''' Wrap :py:meth:`execute` for use via the
            command line. Convert exceptions into
            friendly error messages and typeconvert
            things coming in via CLI args.

            .. todo: Clean up exception handling in ``debug``
                     mode.

            .. note: Calling this method from Python is
                     possible but not recommended - if you
                     use :py:meth:`execute` instead, you can
                     pass native types and exceptions bubble
                     up properly.

            :param **cli: Command line arguments
            (``dict``) passed-in from ``__main__``'s
            :py:mod:`argparse` work.

            :returns: Unix process exit code describing
            the result of the current `Importer` run. If
            the result of :py:meth:`execute` is truthy,
            ``0`` is returned to indicate no error,
            otherwise ``1`` is returned. '''

        self.cli, self.argset, self.debug = True, cli, self.config.get('debug', False)  # setup CLI and debug mode

        try:

            # convert date strings
            try:
                begin, end = _FROM_MIXPANEL_DATE(cli['begin']), _FROM_MIXPANEL_DATE(cli['end'])
            except:  # pragma: nocover
                raise RuntimeError('Failed to parse YYYY-MM-DD begin/end dates.')  # @TODO(sgammon): proper exception handling

            # configure prompts and debug
            self.yes = cli.get('yes', False)

            # configure logging
            if cli['verbose'] > 0:  # if verbose mode is turned on...
                logging.getLogger().setLevel(logging.INFO - (10 * cli['verbose']) - 1)
                self.say('Verbose mode is active. Go more verbose with `-vv` or quiet with `-q`.')

            elif cli['quiet']:  # otherwise, if quiet mode is turned on...

                self.quiet = True  # set local quiet mode to 'on'
                logging.getLogger().setLevel(logging.CRITICAL)

            # dispatch (convert result for use as a Unix exit code)
            self.logging.info('Starting Importer...')
            return 0 if bool(self.execute(begin, end, **{

                'to': _PROVIDER(cli.get('target', self.mixconfig.get('to'))),  # source provider
                'from': _PROVIDER(cli.get('source', self.mixconfig.get('from'))),  # destination provider
                'kinds': cli.get('kinds', self.mixconfig.get('kinds')),  # event kinds to transfer
                'verbose': bool(cli.get('verbose', self.config.get('verbose', False))),  # verbose mode
                'reset_ts': bool(cli.get('reset_ts', self.config.get('reset_timestamps', False))),  # whether to reset timestamps
                'quiet': bool(cli.get('quiet', self.config.get('quiet', False))),  # quiet mode
                'yes': bool(cli.get('yes', self.config.get('yes', False)))  # yes mode

            })) else 1

        except NotImplementedError as e:  # pragma: nocover
            self.logging.error("Stubbed functionality requested.")

            # re-raise in debug mode
            if self.debug:
                import pdb; pdb.set_trace()
                raise

            print ""
            print "Some of the functionality you requested is not yet implemented:"
            print e
            print ""

            return 1

        except RuntimeError as e:  # pragma: nocover
            self.logging.error("Encountered RuntimeError.")

            # re-raise in debug mode
            #if self.debug:
            #    import pdb; pdb.set_trace()
            #    raise
            raise

            print ""
            print "An error was encountered while processing your request:"
            print e
            print ""

            return 1

        except Exception as e:  # pragma: nocover
            self.logging.critical('Unhandled exception occurred. Exiting.')

            # re-raise in debug mode
            #if self.debug:
            #    import pdb; pdb.set_trace()
            #    raise
            raise

            print ""
            print "An unhandled exception was encountered while processing your request:"
            print e
            print ""
