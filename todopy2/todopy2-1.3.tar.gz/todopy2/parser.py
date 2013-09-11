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

from __future__ import print_function


class TodoParser:
    """ To-do file manipulation class.

    Creates and updates to-do file.

    :param options: Parsed program options.
    :type options: dict
    """

    def __init__(self, options):
        self.item_mark = 1
        self.changed = False
        self.options = options
        self.txt = {}
        self.txt['today']  = '---------------------------------\n'
        self.txt['today'] += '|          TODO TODAY           |\n'
        self.txt['today'] += '---------------------------------\n'
        self.txt['soon']  = '---------------------------------\n'
        self.txt['soon'] += '|          TODO SOON            |\n'
        self.txt['soon'] += '---------------------------------\n'
        self.txt['later'] = '---------------------------------\n'
        self.txt['later'] += '|          TODO LATER           |\n'
        self.txt['later'] += '---------------------------------\n'
        self.txt['footer'] = '-' * 88
        self.txt['footer'] += '\n\n'
        self.txt['footer'] += 'LEGEND:\n'
        self.txt['footer'] += '[+]This is a task I have already completed\n'
        self.txt['footer'] += '[.]This is a task I have started but not completed\n'
        self.txt['footer'] += '[ ]This is a task I intend to complete today, soon or later\n'
        self.todo = self.parse_todo(options.config)

    # TODO: refactor me: don't use __del__
    def __del__(self):
        self.save_todo()

    def save_todo(self, force=False):
        if force or self.changed:
            contents = ''
            modes=['today', 'soon', 'later']
            for mode in modes:
                contents += self.txt[mode]
                try:
                    mode_items = self.todo.get(mode, [])
                    for item in mode_items:
                        contents += '['+ item['status'] +'] ' + item['data'] + '\n';
                    contents += '\n'
                except AttributeError:
                    pass
            contents += self.txt['footer']

            file = open(self.options.config, 'w')
            file.write(contents)
            file.close()

    def parse_todo(self, filename):
        """
        Parse txt todo file into a variable.
        """
        todo_data = {}
        try:
            todo_file = open(filename)
            mode = 'today'
            done_parsing = False
            for line in todo_file:
                if line.strip():
                    if line.startswith('-' * 40):
                        done_parsing = True
                    if done_parsing or line.startswith('--'):
                        continue
                    if line.startswith('|'):
                        if 'TODO TODAY' in line:
                            mode = 'today'
                        elif 'TODO SOON' in line:
                            mode = 'soon'
                        elif 'TODO LATER' in line:
                            mode = 'later'
                        continue
                    if (not mode in todo_data):
                        todo_data[mode] = []

                    todo_item = self.parse_todo_item(line.strip())
                    todo_data[mode].append(todo_item)
        except IOError:
            # There is no file, create it.

            self.save_todo(force=True)
        return todo_data

    def parse_todo_item(self, line):
        todo_item = {}
        item_description = line[4:]
        status = line[1:2]
        todo_item['data'] = item_description
        todo_item['status'] = status
        todo_item['mark'] = self.item_mark
        self.item_mark += 1
        return todo_item

    # not used
    def parse_status(self, status_char):
        return {
            ' ': 'todo',
            '.': 'started',
            '+': 'done',
        }[status_char]

    def current(self, modes=['today', 'soon', 'later']):
        out = ''
        for mode in modes:
            empty_block = True
            if self.options.opt_all:
                empty_block = False
            else:
                mode_items = self.todo.get(mode, [])
                for item in mode_items:
                    if item['status'] != '+':
                        empty_block = False
                        continue
            if not empty_block and mode in self.todo:
                if len(self.todo[mode]):
                    out += '\n' + mode.upper() + '\n-----\n'
                for item in self.todo[mode]:
                    if self.options.opt_all or item['status'] != '+':
                        item_desc = item['data']
                        if item['status'] == '+':
                            item_desc = '(DONE) ' + item_desc
                        elif item['status'] == '.':
                            item_desc = '(ON) ' + item_desc
                        out += "%02d" % (item['mark'],) + ': ' + item_desc
                        out += '\n'
        return out

    def mark_item(self, num, mark, title):
        out = ''
        modes=['today', 'soon', 'later']
        for mode in modes:
            if mode in self.todo:
                for item in self.todo[mode]:
                    if item['mark'] == num and item['status'] != mark:
                        # Update tree
                        self.todo[mode].remove(item)
                        item['status'] = mark
                        self.todo[mode].append(item)
                        self.changed = True
                        out = title + ': ' + item['data']
        return out

    def start(self, num):
        return self.mark_item(num, '.', 'Started')

    def reset(self, num):
        return self.mark_item(num, ' ', 'Reset')

    def done(self, num):
        return self.mark_item(num, '+', 'Done')

    def add(self, when, what):
        if when not in ['today', 'soon', 'later']:
            return "Error: please use today, soon or later for time reference"

        item = {}
        item['data'] = what
        item['status'] = ' '
        self.changed = True
        if not when in self.todo:
            self.todo[when] = []
        self.todo[when].append(item)
        return 'Added: ' + what

    def remove(self, num):
        out = ''
        modes=['today', 'soon', 'later']
        for mode in modes:
            if self.todo.get(mode, None):
                for item in self.todo[mode]:
                    if item['mark'] == num:
                        # Update tree
                        self.todo[mode].remove(item)
                        self.changed = True
                        out = 'Removed: ' + item['data']
        return out

    def clean(self):
        out = ''
        items = []
        modes=['today', 'soon', 'later']
        for mode in modes:
            for item in self.todo.get(mode, []):
                if item['status'] == '+':
                    items.append(item['mark'])
                    out += 'Removed: ' + item['data'] + '\n'
        for item in items:
            self.remove(item)
        return out

    def move(self, what, where):
        out = ''
        modes=['today', 'soon', 'later']
        if not where in modes:
            return 'Wrong place to move.'
        for mode in modes:
            for item in self.todo.get(mode, []):
                if item['mark'] == what:
                    self.todo[mode].remove(item)
                    if not self.todo.get(where, False):
                        self.todo[where] = []
                    self.todo[where].append(item)
                    self.changed = True
                    out = 'Moved: ' + item['data']
        return out
