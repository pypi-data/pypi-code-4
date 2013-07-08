#!/usr/bin/env python


import argparse
import os
import subprocess
import shutil
import sys


CHROME_BIN = 'google-chrome'
CHROME_PARAMS = '--user-data-dir='
USER_DIRS = os.path.join(os.environ['HOME'], '.chrome_dirs')

class SpawnChrome(object):
    def __init__(self, args):
        self.my_args = args[0]
        self.chrome_args = args[1]
        if self.my_args.project_name:
            self.project_name = self.my_args.project_name
            self.project_path = os.path.join(USER_DIRS, self.project_name)
        # check if USER_DIRS exists otherwise make it
        if not os.path.exists(USER_DIRS):
            os.path.os.mkdir(USER_DIRS)

    def mk_project_dir(self):
        if not os.path.exists(self.project_path):
            os.path.os.mkdir(self.project_path)

    def spawn_chrome(self):
        # build the base chrome command
        chrome_args = [CHROME_BIN] + [CHROME_PARAMS + self.project_path]
        # add any additional params passed to chrome
        chrome_args += self.chrome_args
        print chrome_args
        subprocess.call(chrome_args)

    def ls_projects(self):
        for p in os.listdir(USER_DIRS):
            print('* %s' % p)

    def rm_project(self, project):
        shutil.rmtree(os.path.join(USER_DIRS, project))


def cli_run():
    """docstring for cli_run"""
    parser = argparse.ArgumentParser(
        description='Spawn a sandboxed chrome instance per project')
    parser.add_argument('-p', '--project-name',
                        help='Project name to spawn a chrome instance for ')
    parser.add_argument('-l', help='List existing chrome project dirs',
                        action='store_true')
    parser.add_argument('-d', '--remove-project',
            help='Removes the corresponding project dir from chrome dirs',
            nargs=1)
    args = parser.parse_known_args()

    if args[0].project_name:
        spawn = SpawnChrome(args)
        spawn.mk_project_dir()
        spawn.spawn_chrome()

    if args[0].l:
        spawn = SpawnChrome(args)
        spawn.ls_projects()

    if args[0].remove_project:
        spawn = SpawnChrome(args)
        spawn.rm_project(args[0].remove_project[0])
    if len(sys.argv) == 1:
        parser.print_help()


if __name__ == '__main__':
    cli_run()
