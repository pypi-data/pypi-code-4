#-*- coding: utf-8 -*-
# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os
import os.path as osp
import glob

from cubicweb.dataimport import SQLGenObjectStore
from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL
from cubicweb import AuthenticationError
from cubicweb import cwconfig
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx

from cubes.dataio.xy import XY
from cubes.dataio import interfaces, dataimport


def _init_cw_connection(appid):
    config = cwconfig.instance_configuration(appid)
    sourcescfg = config.sources()
    config.set_sources_mode(('system',))
    cnx = repo = None
    while cnx is None:
        try:
            login = sourcescfg['admin']['login']
            pwd = sourcescfg['admin']['password']
        except KeyError:
            login, pwd = manager_userpasswd()
        try:
            repo, cnx = in_memory_repo_cnx(config, login=login, password=pwd)
        except AuthenticationError:
            print 'wrong user/password'
        else:
            break
    session = repo._get_session(cnx.sessionid)
    return cnx, session


class ImportRDFCommand(Command):
    """
    Command for importing rdf data
    """
    name = 'import-rdf'
    arguments = '<instance> <directory-or-file>'
    options = [ ('rdf-format', {'type': 'string',
                               'help': 'Rdf format of the files (xml, nt, n3...).', }),
                ('lib', {'type': 'string', 'default': 'rdflib',
                         'help': "Rdf lib to be used (librdf or rdflib or rawnt)", }),
                ]
    acceptable_types = ('xml', 'nt', 'n3', 'rdf')

    def _create_store(self, session, XY):
        external_uris = dict(session.execute('Any U, X WHERE X is ExternalUri, X uri U'))
        internal_store = SQLGenObjectStore(session)
        store = dataimport.RDFStore(session, XY,
                                    internal_store=internal_store,
                                    external_uris_dict=external_uris)
        return store, internal_store

    def _step_flush(self, store, internal_store):
        internal_store.flush()
        internal_store.commit()
        store.flush()

    def _final_flush(self, store, internal_store):
        store.convert_all_relations()
        store.cleanup()

    def run(self, args):
        appid = args.pop(0)
        directory_or_file = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        if self.config.lib == 'rawnt' and self.config.rdf_format != 'nt':
            raise ValueError('Only the nt format is usable with the rawnt reader')
        # Get filenames
        filenames = []
        if osp.isfile(directory_or_file):
            filenames = (directory_or_file,)
        elif osp.isdir(directory_or_file):
            for filename in os.listdir(directory_or_file):
                if filename.rsplit('.', 1)[-1] in self.acceptable_types:
                    filenames.append(osp.join(directory_or_file, filename))
        # Create the internal store and the RDF store
        store, internal_store = self._create_store(session, XY)
        # Push grouped filenames
        for _filenames in self.group_files(filenames):
            uri_dictionnary = interfaces.build_uri_dict(_filenames, library=self.config.lib,
                                                        rdf_format=self.config.rdf_format)
            uri_dictionnary = XY.merge_uri_dictionnary(uri_dictionnary)
            # Import entities
            self.push_uri_dictionnary(store, uri_dictionnary)
            # Flush
            self._step_flush(store, internal_store)
        # Final flush
        self._final_flush(store, internal_store)

    def group_files(self, filenames):
        """ Function that group files according to some specific
        logic.
        Should be overwritten for specific applications.
        """
        yield filenames

    def push_uri_dictionnary(self, store, uri_dictionnary):
        """ Push an uri dictionnary using the store
        """
        for uri, rdf_properties in uri_dictionnary.iteritems():
            entity = store.create_entity(rdf_properties)


CWCTL.register(ImportRDFCommand)
