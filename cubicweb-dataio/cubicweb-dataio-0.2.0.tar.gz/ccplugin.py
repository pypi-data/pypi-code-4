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
                         'help': "Rdf lib to be used (librdf or rdflib)", }),
                ]
    acceptable_types = ('xml', 'nt', 'n3', 'rdf')


    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        directory_or_file = sys.argv[3]
        # Get filenames
        filenames = []
        if osp.isfile(directory_or_file):
            filenames = (directory_or_file,)
        elif osp.isdir(directory_or_file):
            for filename in os.listdir(directory_or_file):
                if filename.rsplit('.', 1)[-1] in self.acceptable_types:
                    filenames.append(osp.join(directory_or_file, filename))
        # Create the RDF store
        uri_dictionnary = interfaces.build_uri_dict(filenames, library=self.config.lib,
                                                    rdf_format=self.config.rdf_format)
        uri_dictionnary = XY.merge_uri_dictionnary(uri_dictionnary)
        # Add internal store
        internal_store = SQLGenObjectStore(session)
        store = dataimport.RDFStore(session, XY,
                                    internal_store=internal_store)
        # Import entities
        for uri, rdf_properties in uri_dictionnary.iteritems():
            entity = store.create_entity(rdf_properties)
        # Flush
        internal_store.flush()
        internal_store.commit()
        store.flush()
        # Final flush
        store.convert_all_relations()
        store.cleanup()


CWCTL.register(ImportRDFCommand)

