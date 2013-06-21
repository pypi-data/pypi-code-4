# -*- coding: utf-8 -*-
from __future__ import with_statement

import hashlib
import htmlentitydefs
import cPickle as pickle
import logging
import random
import re
import os
import sys
import urllib
import zlib

from decimal import Decimal
from itertools import islice

from django.db.models import AutoField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.utils.html import strip_tags

from pwutils.lockfile import FileLock, AlreadyLocked, LockTimeout, NotMyLock

logger = logging.getLogger(__name__)

USE_CELERY = getattr(settings, 'USE_CELERY', False)
if USE_CELERY:
    from celery.task import task, periodic_task
    from celery.task.sets import subtask


def copy_model_instance(obj):
    initial = copy_model_initial(obj)
    return obj.__class__(**initial)


def copy_model_initial(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return initial

my_secret = settings.SECRET_KEY


def encode_data(data):
    """Turn `data` into a hash and an encoded string,
    suitable for use with `decode_data`."""
    text = zlib.compress(pickle.dumps(data, 0)).encode('base64')\
                                               .replace('\n', '')
    md5code = hashlib.md5(my_secret + text).hexdigest()
    return md5code, text


def decode_data(hash, enc):
    """The inverse of `encode_data`."""
    text = urllib.unquote(enc)
    md5code = hashlib.md5(my_secret + text).hexdigest()
    if md5code != hash:
        raise Exception("Bad hash!")
    data = pickle.loads(zlib.decompress(text.decode('base64')))
    return data


def create_generic_filter(obj,
                          ct_field_name='content_type',
                          obj_id_field_name='object_id'):

    ctype = ContentType.objects.get_for_model(obj)
    filter_dict = {ct_field_name: ctype, obj_id_field_name: obj.id}
    return filter_dict


def average(values):
    """Computes the arithmetic mean of a list of numbers.

    >>> print average([20, 30, 70])
    40.0
    """
    try:
        return sum(values, 0.0) / len(values)
    except ZeroDivisionError:
        return 0


def dynamic_import(names):
    imported = []
    for name in names:
        # Use rfind rather than rsplit for Python 2.3 compatibility.
        lastdot = name.rfind('.')
        modname, attrname = name[:lastdot], name[lastdot + 1:]
        mod = __import__(modname, {}, {}, [''])
        imported.append(getattr(mod, attrname))
    return imported


def lowpriority():
    """ Set the priority of the process to below-normal."""

    try:
        sys.getwindowsversion()  # @UndefinedVariable
    except:
        is_windows = False
    else:
        is_windows = True

    if is_windows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        try:
            import win32api
            import win32process
            import win32con  # @UnresolvedImport
        except ImportError:
            pass
        else:
            pid = win32api.GetCurrentProcessId()
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,
                                          True, pid)
            win32process.SetPriorityClass(handle,
                             win32process.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        os.nice(1)


def paginate(objects, request=None,
             count=getattr(settings, 'ITEMS_PER_PAGE', 20)):

    paginator = Paginator(objects, count)

    try:
        page_num = int(request.REQUEST['page'])
    except (KeyError, ValueError):
        page_num = 1

    try:
        page = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    return page

digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def generate_sequence(n_items):
    for temp in range(1, n_items):
        yield digits[random.randint(0, 9)]


class NavItem(object):

    title = u'БезНазвания'
    url = '#'

    def __init__(self, title=None, url=None, **kwargs):

        if title is not None:
            self.title = title
        if url is not None:
            self.url = url

        self.__dict__.update(kwargs)

    def __unicode__(self):
        return u'<NavItem %s>' % self.title

    def __repr__(self):
        return '<NavItem %s>' % repr(self.title)

    def get_absolute_url(self):
        return self.url

    get_url = get_absolute_url


#main_page = NavItem(title=u'Главная', url=reverse('main_page'))

class NavMenu(list):

    def get_navigation_path(self):
        return self

    def extend(self, parts):
        extend = super(NavMenu, self).extend
        if hasattr(parts, 'get_navigation_path'):
            extend(parts.get_navigation_path())
        else:
            extend(parts)


def check_float(value):

    if isinstance(value, (int, float, Decimal)):
        return True
    else:
        try:
            value = unicode(value).replace(',', '.')
            float(value)
        except (TypeError,
                ValueError,
                UnicodeEncodeError):
            return False
        else:
            return True


def parse_decimal(value, safe=False):

    if safe and not check_float(value):
        return None
    return Decimal(unicode(value).replace(',', '.').strip())


class FakeTask(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        return self(*args, **kwargs)

    def apply_async(self, args=None, kwargs=None, *temp, **options):
        args = args or []
        kwargs = kwargs or {}
        return self(*args, **kwargs)


def celery_task(*args, **kwargs):
    def _decorator(func):
        if USE_CELERY:
            kwargs.setdefault('queue', getattr(settings,
                                               'CELERY_DEFAULT_QUEUE',
                                               'celery')
                             )
            return task(*args, **kwargs)(func)
        else:
            return FakeTask(func)
    return _decorator


def celery_periodic_task(*args, **kwargs):
    def _decorator(func):
        if USE_CELERY:
            kwargs.setdefault('queue', getattr(settings,
                                               'CELERY_DEFAULT_QUEUE',
                                               'celery')
                             )
            return periodic_task(*args, **kwargs)(func)
        else:
            return FakeTask(func)
    return _decorator


def celery_subtask(task=None, args=None, kwargs=None, options=None, **ex):
    if USE_CELERY:
        options = options or {}
        options.setdefault('queue', getattr(settings,
                                            'CELERY_DEFAULT_QUEUE',
                                            'celery')
                         )
        return subtask(task, args=args,
                             kwargs=kwargs,
                             options=options,
                             **ex)
    else:
        # TODO store additional args and kwargs in fake task
        if not isinstance(task, FakeTask):
            task = FakeTask(task)
        return task


def get_current_site_url():

    domain = Site.objects.get_current().domain
    return 'http://%s' % domain


def chunks(seq, size):
    """ Yield successive n-sized chunks from seq.
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def ichunks(iterable, size):
    # XXX needed to list conversion
    return iter(lambda it=iter(iterable): list(islice(it, size)), [])


class PWFileLock(FileLock):
    def __enter__(self):
        logger.debug("acquiring lock...")
        try:
            self.acquire(getattr(settings, 'LOCK_WAIT_TIMEOUT', 10))
        except AlreadyLocked:
            logger.warning("lock already in place. quitting.")
            return
        except LockTimeout:
            logger.warning("waiting for the lock timed out. quitting.")
            return

        logger.debug("acquired.")
        return self

    def __exit__(self, *etc_):
        logger.debug("releasing lock...")
        try:
            self.release()
        except NotMyLock:
            pass  # do nothing
        logger.debug("released.")


class EmptyContext(object):
    def __enter__(self):
        return self

    def __exit__(self, *etc_):
        pass

    def __call__(self):
        return self


def unescape(text):
    def fixup(match):
        text = match.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def strip_html(text):

    text = text.replace('<br />', '\n')
    text = strip_tags(text)
    return unescape(text.strip())
