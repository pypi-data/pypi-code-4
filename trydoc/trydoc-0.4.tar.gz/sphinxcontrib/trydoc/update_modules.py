#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
# Copyright (C) 2013 NaN·tic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

import ConfigParser
import argparse
import sys
import os.path
from proteus import config as pconfig, Model


def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    parser.add_argument('--config-file', '-c', dest='config',
        default='modules.cfg',
        help='Config File to update modules (default: ./modules.cfg)')
    parser.add_argument('--trytond-dir', '-t', dest='trytond',
        help='Path to the trytond directory if it is not installed as a module')

    settings = parser.parse_args()
    return settings


def main(argv=sys.argv):
    options = parse_arguments(sys.argv)

    if options.trytond:
        directory = os.path.abspath(os.path.normpath(options.trytond))
        if os.path.isdir(directory):
            sys.path.insert(0, directory)

    pconfig.set_trytond(options.database, database_type='postgresql',
        password='admin')

    Module = Model.get('ir.module.module')
    modules = Module.find([('state', '=', 'installed')])

    config = ConfigParser.ConfigParser()
    f = open(options.config, 'rw')
    config.readfp(f)
    f.close()

    modules = [module.name for module in modules]

    op = config.options('modules')

    for module in modules:
        if module in op:
            continue
        print module
        config.set('modules', module, True)

    with open(options.config, 'wb') as configfile:
            config.write(configfile)
