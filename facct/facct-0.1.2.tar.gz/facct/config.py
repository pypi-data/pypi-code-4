#!/usr/bin/python
#-*- coding: utf-8 -*-

# Copyright (c) 2013 Eric F <efigue> Figerson
# Author(s):
#   Eric F <eric.foss@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse
import datetime

from facct.i18n import _
import facct.path_mngt as path_mngt
try: import ConfigParser as configparser # Python 2
except: import configparser # Python 3

appli_name = path_mngt.appli_name
conf_file = os.path.join(os.path.expanduser('~'), '.%s.rc' % appli_name)
if not os.path.exists(conf_file):
    open(conf_file, 'w').close()

config = configparser.RawConfigParser(allow_no_value=True)
config.readfp(open(conf_file))


def initialized():
    return (len(config.sections()) > 0)

def add(orga, silent=False):
    if not config.has_section(orga):
        config.add_section(orga)
    else:
        if not silent:
            sys.stderr.write(_('Section %s: already presents\n') % orga)

def request_user(orga, default):
    good_path = False
    while not good_path:
        sys.stderr.write(_('Give a path to store data for your') +\
                _(' organization {0} : [{1}]').format( orga, default))
        try:
            path = raw_input()
            good_path = True
        except:
            sys.exit(2)
        if not path:
            path = default
        if not path == default:
            good_path = (os.path.exists(os.path.dirname(path)))
        if not good_path:
            sys.stderr.write(_('%s no such directory\n') % os.path.dirname(path))
    return path

def initialize(orga, auto=False):
    if not orga:
        sys.stderr.write(_('No organization given, exit\n'))
        sys.exit(2)
    default = os.path.join(os.path.expanduser('~'), appli_name, orga)
    path = default
    if not auto:
        path = request_user(orga, default)
    add(orga, silent=True)
    config.set(orga, 'root', path)
    config.set(orga, 'accounts', os.path.join(path, 'accounts'))
    config.set(orga, 'bills', os.path.join(path, 'bills'))
    config.set(orga, 'data', os.path.join(path, 'data'))
    with open(conf_file, 'w') as configfile:
        config.write(configfile)
    return True


def check(organization=''):
    if len(config.sections()) == 0:
        sys.stderr.write(_('No configuration file or empty file!\n'))
        sys.exit(2)
    if not organization:
        if not len(config.sections()) == 1:
            sys.stderr.write(_('Please give organisation name (%s).\n'
                        ).format( _(' or ').join(config.sections())))
            sys.exit(2)
        organization = config.sections()[0]
    if organization not in config.sections():
        sys.stderr.write(_('organization {0} not in configurations ({1}).\n'
            ).format(organization, _(' or ').join(config.sections())))
        sys.exit(2)
    return organization

def get_value(key, organization=''):
    if not config.has_section(organization):
        sys.stderr.write(_('section "{0}" does not exist in {1}\n'
            ).format(organization, conf_file))
        sys.exit(2)
        return ''
    if not config.has_option(organization, key):
        return ''
    return config.get(check(organization), key)

def get_accounts_dir(organization=''):
    return get_value('accounts', organization)

def get_bills_dir(organization=''):
    return get_value('bills', organization)

def get_data_dir(organization=''):
    return get_value('data', organization)

def get_root_app():
    return path_mngt.get_root_app()

def get_bench_infra_dir():
    return os.path.join(get_root_app(), 'bench_infra')

def get_internal_data_dir():
    return os.path.join(get_root_app(), 'data')

def get_share_dir():
    return path_mngt.get_share_dir()

def get_args(bill_name=False, year=False, create=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-b', '--bench', dest='bench',
            action='store_true', default=False, help=_('private bench directory'))
    parser.add_argument('-o', '--orga', dest='orga', nargs='?', default='',
            help=_('organisation name'))
    parser.add_argument('-d', '--dir', dest='account_dir', nargs='?',
            default='.', help=_('account directory'))
    if bill_name:
        parser.add_argument('bill_name', help=_('CSV bill file'))
    if year:
        parser.add_argument('-y', '--year', type=int, dest='year', nargs='?',
                default=datetime.date.today().year, help=_('account year'))
    if create:
        parser.add_argument('-c', dest='create', action='store_true',
                default=False, help=_('organisation to create'))
    return parser.parse_args()

