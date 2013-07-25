# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
import sys
from optparse import make_option

import elementflow

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

if not getattr(settings, 'SPHINX_ROOT', False):
    raise ImportError('You need to set SPHINX_ROOT'
                      ' in django settings file')
from djangosphinx.apis.current import (SphinxClient,
                                       SPH_MATCH_EXTENDED,
                                       SPH_SORT_RELEVANCE)

from pwutils.utils import PWFileLock, lowpriority

from base import BaseSearchEngine


logger = logging.getLogger(__name__)


class SphinxSearch(BaseSearchEngine):

    _connection = None

    index = '*'

    STOP_SYMBOLS = ['-', '/', '\\', '*', '"', '"', '+']

    def make_query(self, query):
        tokens = query.split(' ')
        result = []
        for token in tokens:
            for c in self.STOP_SYMBOLS:
                token = token.replace(c, ' ')
            result.append(token)
        query = u' '.join(result)
        return query

    def get_connection(self):
        if self._connection is None:
            con = self._connection = SphinxClient()
            con.SetServer(settings.SPHINX_SERVER, getattr(settings,
                                                          'SPHINX_PORT',
                                                          None))
            con.SetMatchMode(SPH_MATCH_EXTENDED)
            con.SetSortMode(SPH_SORT_RELEVANCE)
            con.SetLimits(0,1000)
        return self._connection

    def get_results(self, query):

        con = self.get_connection()
        results = con.Query(self.make_query(query),
                            index=self.index)

        err = con.GetLastError()
        if err:
            logger.error(err)
            logging.getLogger('sentry.errors').error(err)
            con._reqs = [] # XXX
        return results


class SphinxSchema(object):
    def __init__(self, schema, items, time_attrs=None, text_attrs=None,
                 output=None):
        self.schema = schema
        self.items = items
        self.time_attrs = time_attrs
        self.text_attrs = text_attrs
        self.output = output

    def __iter__(self):
        return iter(self.items)

    def get(self, name, default=None):
        if name in ['schema', 'time_attrs', 'text_attrs']:
            return getattr(self, name) or default
        return default
    pop = get

    def __getitem__(self, name):
        return self.get(name)

    def items(self):
        return iter(self)

    def generate(self):
        return generate_xml(self, self.output)


def generate_xml(object_dict, outfile=None):
    # XXXXX move to SphinxShema class
    if outfile is None:
        outfile = sys.stdout

    with elementflow.xml(outfile, u'sphinx:docset') as xml:
        # schema generation
        with xml.container('sphinx:schema') as xml:
            for key in object_dict['schema']:
                xml.element('sphinx:field', attrs={'name': key})
            for key in object_dict.get('time_attrs', []):
                xml.element('sphinx:attr', attrs={'name': key,
                                                  'type': 'timestamp'})
            for key in object_dict.get('text_attrs', []):
                xml.element('sphinx:attr', attrs={'name': key,
                                                  'type': 'str2ordinal'})

        object_dict.pop('schema')
        object_dict.pop('time_attrs', None)
        object_dict.pop('text_attrs', None)

        # fill values
        for oid, item in object_dict.items():
            with xml.container('sphinx:document', attrs={'id': oid}) as xml:
                for key, value in item.items():
                    xml.element(key, text=value)
    return outfile


class SphinxGenCommand(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-o', '--output',
                    action='store',
                    type='string',
                    dest='output',
                    help='output file'),
        )

    def handle(self, schema, *args, **options):

        generate = getattr(self, 'generate_data_%s' % schema, None)
        if generate is None:
            raise CommandError('unknown schema: %s' % schema)

        logger.info('lowpriority')
        lowpriority()

        with PWFileLock('sphinx_%s' % schema) as lock:
            if lock is None:
                return

            filename = options.get('output')

            if filename is None:
                out_file = sys.stdout
                need_close = False
            else:
                try:
                    out_file = file(filename, 'w')
                except IOError:
                    raise CommandError('bad file %s' % filename)
                need_close = True

            try:
                generate(out_file)
            finally:
                if need_close:
                    out_file.close()
