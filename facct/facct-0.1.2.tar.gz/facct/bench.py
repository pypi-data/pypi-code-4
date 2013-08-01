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
import glob
import filecmp
import datetime
import shutil

import facct.generate_all as generate_all
import facct.config as config
import facct.init_year as init_year
import facct.bill.gen_tex as gen_tex
import facct.db.init_clients as init_clients

def are_dir_trees_diff(dir1, dir2):
    """
        Compare two directories recursively. Files in each directory are
        assumed to be equal if their names and contents are equal.

        @param dir1: First directory path
        @param dir2: Second directory path

        @return: False if the directory trees are the same and
        there were no errors while accessing the directories or files,
        True otherwise.
        """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or \
        len(dirs_cmp.funny_files)>0:
        return True
    (_, mismatch, errors) =  filecmp.cmpfiles(
                dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch)>0 or len(errors)>0:
        return True
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if are_dir_trees_diff(new_dir1, new_dir2):
            return True
    return False

def get_script_root():
    return os.path.abspath(os.path.dirname(__file__))

debug = False
def redirect_stdout_func(func, *args):
    sav_stdout = sys.stdout
    f = open(os.devnull, 'w')
    sys.stdout = f
    if debug:
        sys.stdout = sys.stderr
    ret = func(*args)
    f.close()
    sys.stdout = sav_stdout

def initialize_corp_ref(orga='corp_ref'):
    if not config.initialized():
        config.initialize(orga, auto=True)
    dest = config.get_value('root', orga)
    if not os.path.exists(dest):
        shutil.copytree(os.path.join(config.get_bench_infra_dir(), orga), dest)

def bench_ledger_generation(orga, bench):
    for d in sorted(glob.glob(os.path.join(
                    config.get_accounts_dir(orga), '2*'))):
        year = os.path.basename(d)
        redirect_stdout_func(generate_all.main, orga, d)
        if bench:
            bmk_dir = os.path.join(config.get_accounts_dir(orga),
                    'private_bench', year)
        else:
            bmk_dir = os.path.join(config.get_bench_infra_dir(),
                    'benchs', 'accounts', year)
        bmk_dir = os.path.abspath(bmk_dir)
        if not os.path.exists(bmk_dir):
            sys.stderr.write('[KO] benchmark %s not found!\n' % bmk_dir)
            continue
        if not are_dir_trees_diff(d, bmk_dir):
            print('[OK] %s %s account: no differences with benchmark' % (
                        orga, year))
        else:
            print(
                '[KO] %s %s account: differences with benchmark' % (orga, year))
            if debug:
                print ('d=%s bmk_dir=%s'% (d, bmk_dir))


def bench_bill_generation(orga):
    bill_date = '022013'
    one_bill = os.path.join(
            config.get_bills_dir(orga), '2013', bill_date+'.csv')
    if not redirect_stdout_func(gen_tex.main, orga, one_bill):
        print('[OK] %s %s bill.' % (orga, bill_date))
    else:
        print('[KO] %s %s bill.' % (orga, bill_date))

def bench_year_initialization(orga, year):
    new_dir = os.path.join(config.get_accounts_dir(orga), '%s' % year)
    to_remove = (not os.path.exists(new_dir))

    if not redirect_stdout_func(init_year.main, orga, year, False):
        print('[OK] %s %s init_year.' % (orga, year))
    else:
        print('[KO] %s %s init_year.' % (orga, year))
    bench_text = '%s: already exists\n' % new_dir
    if bench_text == init_year.main(orga, year, False):
        print('[OK] %s %s already exists.' % (orga, year))
    else:
        print('[KO] %s %s does not exist.' % (orga, year))
    if to_remove and os.path.exists(new_dir):
        shutil.rmtree(new_dir)
    new_dir_init = os.path.join(config.get_accounts_dir(orga), '%s' % year)
    if new_dir_init and not new_dir == year and os.path.exists(new_dir_init):
        shutil.rmtree(new_dir_init)

def bench_initialization(orga):
    if orga == 'corp_ref':
        initialize_corp_ref()
    present_years = []
    accounts_dir = config.get_accounts_dir(orga)
    if accounts_dir:
        glob_pattern = os.path.join(accounts_dir, '2*')
        present_years = sorted(glob.glob(glob_pattern))
    if present_years:
        last_dir = present_years[-1]
    else:
        root_dir = config.get_value('root', orga)
        year = datetime.datetime.today().year
        last_dir = os.path.join(root_dir, '%s' % year)
    last_year = os.path.basename(last_dir)
    new_year = int(last_year)+1
    bench_year_initialization(orga, new_year)
    bench_year_initialization(orga, new_year+2)

def bench_db_initialization(orga):
    if not redirect_stdout_func(init_clients.main, orga):
        print('[OK] %s db.' % orga)
    else:
        print('[KO] %s db.' % orga)

def main(orga='', bench=False):
    bench_initialization(orga)
    bench_ledger_generation(orga, bench)
    bench_bill_generation(orga)
    bench_db_initialization(orga)

if __name__ == "__main__":
    args = config.get_args()
    sys.exit(main(args.orga, args.bench))
