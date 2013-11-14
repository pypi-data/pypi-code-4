# -*- coding: UTF-8 -*-
from __future__ import print_function
from collections import namedtuple
from importlib import import_module
from logging import getLogger
from math import ceil
from operator import attrgetter
from re import search
from textwrap import dedent
from threading import Thread, Lock

import lxml.html.clean
from requests import Session, RequestException
from requests.utils import default_user_agent
import yaml

from .exceptions import ConfigurationError, SiteException, NotificationException, LoginError
from .utils import current_time, sleep, urlencode_utf8
from .version import __version__


UA_STRING = (
    'WebAlerts/{version} (+https://github.com/clee704/WebAlerts) '
    '{requests_ua_string}'
).format(version=__version__, requests_ua_string=default_user_agent())


class App(object):
    """
    Returns a WebAlerts app object. It is initialized with configuration values
    in a :py:class:`dict` object. For the list of config values, see
    `Configuration options`_.

    .. attribute: logger

       Logger for this class

    """

    DEFAULT_VALUES = {
        'patterns': None,
        'check_interval': 5,
        'notify_interval': 5,
    }

    def __init__(self, config=None):
        self.logger = getLogger(__name__).getChild(self.__class__.__name__)
        self.config = dict(App.DEFAULT_VALUES)
        if config:
            self.config.update(config)
        self.sites = None
        self.notifications = None
        self._start = None

    def from_yaml(self, name):
        """
        Loads config values from a YAML file.

        """
        with open(name) as f:
            self.config.update(yaml.load(f))

    def _init_site_data(self):
        self.sites = {}
        if not isinstance(self.config.get('sites'), dict):
            raise ConfigurationError('sites should be dict')
        for name, config in self.config['sites'].iteritems():
            if not config:
                continue
            try:
                cls = config['class']
            except KeyError:
                raise ConfigurationError('class should be defined for sites')
            if isinstance(cls, basestring):
                import_name = cls
                cls = self._import_class(import_name)
                if cls is None:
                    msg = 'Site %s is not added as it could not be imported'
                    self.logger.warning(msg, name)
                    continue
            try:
                instance = cls(config)
            except SiteException as e:
                self.logger.warning('Site %s is not added due to an error: %s', name, e)
            else:
                self.sites[name] = {
                    'instance': instance,
                    'config': config,
                    'counter': 0,
                    'errors': 0,
                    'disabled': False,
                }
                self.logger.info('Site %s is added', name)

    def _init_notification_data(self):
        self.notifications = {}
        if not isinstance(self.config.get('notifications'), dict):
            raise ConfigurationError('notifications should be dict')
        for name, config in self.config['notifications'].iteritems():
            if not config:
                continue
            try:
                cls = config['class']
            except KeyError:
                raise ConfigurationError('class should be defined for notifications')
            if isinstance(cls, basestring):
                import_name = cls
                cls = self._import_class(import_name)
                if cls is None:
                    msg = 'Notification %s is not added as it could not be imported'
                    self.logger.warning(msg, name)
                    continue
            try:
                instance = cls(config)
            except NotificationException as e:
                self.logger.warning('Notification %s is not added due to an error: %s', name, e)
            else:
                self.notifications[name] = {
                    'instance': instance,
                    'config': config,
                    'counter': 0,
                    'posts': [],
                    'lock': Lock(),
                }
                self.logger.info('Notification %s is added', name)

    def run(self):
        """
        Starts the main loop of the app that periodically collects new posts and
        feeds those posts to notification services.

        """
        g = self._run()
        while True:
            try:
                next(g)
            except StopIteration:
                break

    def _run(self):
        try:
            self._init_site_data()
            self._init_notification_data()
            self._start = current_time()
            while self.sites:
                self.logger.debug('Main loop started')
                yield self._loop_body()
                # +0.1 is needed as the accuracy of time.sleep() is not so great
                # and it may wake up too early, causing the next delay too short
                delay = 60 - (current_time() - self._start) % 60 + 0.1
                self.logger.debug('Sleeping for %f seconds', delay)
                sleep(delay)
            self.logger.info('No site to visit')
        except KeyboardInterrupt:
            self.logger.info('Interrupted')
            # Make the shell prompt printed on the next line.
            print()
        except Exception:
            self.logger.exception('Crashed due to an uncaught error')

    def _loop_body(self):
        run_in_parallel([App.SiteThread(self, name) for name in self.sites])
        run_in_parallel([App.NotificationThread(self, name) for name in self.notifications])

    def _import_class(self, name):
        try:
            mname, cname = name.rsplit('.', 1)
            return getattr(import_module(mname), cname)
        except (ValueError, ImportError, AttributeError):
            self.logger.exception('Failed to import %s', name)

    class SiteThread(Thread):

        def __init__(self, app, name):
            super(App.SiteThread, self).__init__()
            self.app = app
            self.name = name

        def run(self):
            try:
                self._before_visit()
            except Exception:
                self.app.logger.exception('Site %s crashed due to an uncaught error', self.name)

        def _before_visit(self):
            app = self.app
            data = app.sites[self.name]

            # Do not proceed if it is disabled due to too many errors
            if data['disabled']:
                app.logger.debug('Site %s is disabled', self.name)
                return

            # Increment the counter and visit the site if it exceeds the interval
            data['counter'] += 1
            interval = ceil(max(1, data['config'].get('check_interval',
                    app.config['check_interval'])))
            if data['counter'] >= interval:
                data['counter'] = 0
                app.logger.info('Visiting site %s', self.name)
                self._visit()
            else:
                app.logger.debug('%s loop counter: %d/%d', self.name, data['counter'], interval)

        def _visit(self):
            app = self.app
            site = app.sites[self.name]['instance']
            site_config = app.sites[self.name]['config']

            # Get new posts
            try:
                posts = site.get_new_posts()
            except SiteException as e:
                app.logger.warning('Error in %s: %s', self.name, e)
                app.sites[self.name]['errors'] += 1
                # Disable the site if errors occur 10 times in a row
                if app.sites[self.name]['errors'] >= 10:
                    app.sites[self.name]['disabled'] = True
                    app.logger.warning('Site %s is disabled due to too many errors', self.name)
                return

            # Reset the error counter if success
            app.sites[self.name]['errors'] = 0

            # Find matching posts
            patterns = site_config.get('patterns', app.config.get('patterns', []))
            app.logger.debug('%s: patterns: %s', self.name, patterns)
            posts_matched = [post for post in posts
                    if (patterns is None or
                        any(search(pattern, post.title) or search(pattern, post.content)
                            for pattern in patterns))]
            app.logger.debug('%s: number of checked posts: %d', self.name, len(posts))
            app.logger.debug('%s: number of matched posts: %d', self.name, len(posts_matched))

            # Add matching posts to notifications
            notification_names = site_config.get('notifications', app.notifications.keys())
            app.logger.debug('%s: notification names: %s', self.name, notification_names)
            for noti_name in notification_names:
                if noti_name not in app.notifications:
                    app.logger.warning('%s: notification %s does not exist',
                            self.name, noti_name)
                    continue
                with app.notifications[noti_name]['lock']:
                    app.notifications[noti_name]['posts'].extend(posts_matched)
                    app.notifications[noti_name]['posts'].sort(key=attrgetter('published'))

    class NotificationThread(Thread):

        def __init__(self, app, name):
            super(App.NotificationThread, self).__init__()
            self.app = app
            self.name = name

        def run(self):
            try:
                self._before_notify()
            except Exception:
                self.app.logger.exception('Notification %s crashed due to an uncaught error',
                        self.name)

        def _before_notify(self):
            app = self.app
            data = app.notifications[self.name]

            data['counter'] += 1
            interval = ceil(max(1, data['config'].get('notify_interval',
                    app.config['notify_interval'])))
            if data['counter'] >= interval:
                data['counter'] = 0
                app.logger.info('Notifying with %s', self.name)
                self._notify()
            else:
                app.logger.debug('%s loop counter: %d/%d', self.name, data['counter'], interval)

        def _notify(self):
            app = self.app
            notification = app.notifications[self.name]['instance']
            with app.notifications[self.name]['lock']:
                posts = app.notifications[self.name]['posts']
                try:
                    notification.notify(posts)
                except NotificationException as e:
                    app.logger.warning('Error in %s: %s', self.name, e)
                posts[:] = []


PostBase = namedtuple('Post', 'url title content content_html author author_id published')
class Post(PostBase):
    """
    Represents a generic post, a user's content published to a website.
    String parameters containing non-ASCII characters must be unicode.

    :param url: URL of a post (required).
    :param title: Title of a post (required).
    :param content: Content of a post (required).
    :param author: Name of the original poster of a post
    :param author_id: ID that uniquely identifies the original poster
    :param published: :py:class:`~datetime.datetime` object containing the date
                      and time when a post was published

    """

    __cleaner__ = lxml.html.clean.Cleaner()
    __cleaner__.allow_tags = frozenset(['a', 'b', 'blockquote', 'code', 'del',
        'dd', 'dl', 'dt', 'em', 'h1', 'i', 'img', 'kbd', 'li', 'ol', 'p', 'pre',
        's', 'sup', 'sub', 'strong', 'strike', 'ul', 'br', 'hr',
    ])
    __cleaner__.kill_tags = frozenset(['style'])
    __cleaner__.remove_unknown_tags = False
    __cleaner__.safe_attrs = frozenset([
        'src', 'width', 'height', 'alt', 'title',  # img
        'href', 'title',  # a
    ])

    def __new__(cls, url, title, content, content_html=None,
                author=None, author_id=None, published=None):
        return super(Post, cls).__new__(cls, url, title, content, content_html,
                author, author_id, published)

    @property
    def content_html_safe(self):
        """
        A sanitized version of *content_html*. Notifications should use this
        value instead of *content_html*.

        """
        if self.content_html is None:
            return None
        return Post.__cleaner__.clean_html(self.content_html)

    def __unicode__(self):
        summary = self.content if len(self.content) <= 80 else self.content[:79] + u'…'
        return dedent(u"""\
            Post URL: {post.url}
            Subject: {post.title}
            Published: {post.published}
            Author: {post.author} ({post.author_id})
            {summary}
        """).format(post=self, summary=summary) + ("=" * 79)


class Browser(object):

    # Subclass should define these values
    BASE_URL = None
    QUERY_PATHS = None

    def __init__(self, username=None, password=None):
        self._session = Session()
        self._session.headers.update({'User-Agent': UA_STRING})
        self._username = username
        self._password = password

    def get_page(self, name, **kwargs):
        path, query_map = self.QUERY_PATHS[name]
        url = self.BASE_URL + path
        if query_map:
            expected_keys = query_map.viewkeys()
            provided_keys = kwargs.viewkeys()
            if not (expected_keys & provided_keys):
                raise ValueError('arguments mismatch: expected {0}, got {1}'.format(
                        list(expected_keys), list(provided_keys)))
            url += '?' + urlencode_utf8((query_map[k], kwargs[k]) for k in expected_keys)
        response = self._request_with_login(url)
        return response

    def login(self, username=None, password=None):
        username = self._username if username is None else username
        password = self._password if password is None else password
        if username is None or password is None:
            raise LoginError('Username or password is not provided')
        self._login(username, password)

    def _request_with_login(self, url):
        first_attempt = True
        while True:
            response = self._request(url)
            if not self._login_required(response):
                return response
            if first_attempt:
                self.login()
                first_attempt = False
            else:
                raise LoginError()

    def _request(self, url, method='get', data=None):
        try:
            response = self._session.request(method, url, data=data)
            response.raise_for_status()
        except RequestException as e:
            raise SiteException(e)
        else:
            return Response(response.url, response.content, response.status_code)

    def _login(self, username, password):
        raise NotImplementedError('Subclass should implement this method')

    def _login_required(self, response):
        raise NotImplementedError('Subclass should implement this method')


class Response(object):

    def __init__(self, url, content, status_code):
        self.url = url
        self.content = content
        self.status_code = status_code

    def __repr__(self):
        return '<Response [{0}]>'.format(self.status_code)


def run_in_parallel(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
