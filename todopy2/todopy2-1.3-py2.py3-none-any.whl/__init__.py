#!/usr/bin/env python
#
# To-do file parser
#
# Copyright (C) 2011  Nikola Kotur <kotnick@gmail.com>
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
#
# TODO:
#
# Error handling
# Program configuration in ~/.todopyrc

from __future__ import print_function

import argparse
import sys
from os.path import expanduser

from .parser import TodoParser

def main():
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file location",
                        default="%s/todo.log" % expanduser("~"))
    subparsers = parser.add_subparsers(
        dest="action", help='commands, use [command -h] to get additional help'
    )

    # Listing to-do items.
    list_parser = subparsers.add_parser("ls", help='list to-do items')
    list_parser.add_argument("-a", "--all", action="store_true",  dest="opt_all",
                  help="show all tasks")
    list_parser.add_argument("-t", "--today", action="store_const",
                  dest="opt_today", const="today",
                  default=None, help="show today")
    list_parser.add_argument("-s", "--soon", action="store_const",
                  dest="opt_soon", const="soon",
                  default=None, help="show soon")
    list_parser.add_argument("-l", "--later", action="store_const",
                  dest="opt_later", const="later",
                  default=None, help="show later")

    # Start to-do item.
    start_parser = subparsers.add_parser("start", help="start to-do item")
    start_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Reset to-do item.
    reset_parser = subparsers.add_parser("reset", help="reset to-do item")
    reset_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Mark to-do item as done.
    done_parser = subparsers.add_parser("done", help="mark to-do item as done")
    done_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Remove to-do item.
    remove_parser = subparsers.add_parser("remove", help="remove to-do item")
    remove_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Clean to-do items.
    subparsers.add_parser("clean", help="remove all done to-do items")

    # Add to-do item.
    add_parser = subparsers.add_parser("add", help="add to-do item")
    add_parser.add_argument("when", action="store", help="list to add to, one of: [today | soon | later]")
    add_parser.add_argument("desc", action="store", help="to-do item description, enclose in quotes")

    # Move to-do item.
    move_parser = subparsers.add_parser("move", help="move to-do item")
    move_parser.add_argument("item", action="store", help="number of to-do item", type=int)
    move_parser.add_argument("where", action="store", help="list to move to, one of: [today | soon | later]")

    parameters = sys.argv[1:]
    options = parser.parse_args(parameters if parameters else [ "ls" ])

    todo = TodoParser(options);

    if options.action == "ls":
        modes = []
        if (not options.opt_today and not options.opt_soon and not options.opt_later):
            modes = ['today', 'soon', 'later']
        if options.opt_today:
            modes.append('today')
        if options.opt_soon:
            modes.append('soon')
        if options.opt_later:
            modes.append('later')
        print(todo.current(modes))
    else:
        if options.action == 'start':
            ret_str = todo.start(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'reset':
            ret_str = todo.reset(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'done':
            ret_str = todo.done(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'remove':
            ret_str = todo.remove(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'add':
            ret_str = todo.add(options.when, options.desc)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'clean':
            ret_str = todo.clean()
            if len(ret_str) == 0:
                print("Nothing done.")
            else:
                print(ret_str)
        elif options.action == 'move':
            ret_str = todo.move(options.item, options.where)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
