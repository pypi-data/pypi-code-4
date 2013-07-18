#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import inspect


class Cue(object):
    def __init__(self, script, key, message, default, choices, required_if=None):
        self.script = script
        self.key = key
        self.message = message
        self.default = default
        self.choices = choices
        self.required_if = required_if

    def run_default(self):
        default_value = None
        if self.default is not None:
            default_value = self.get_default()
            sys.stdout.write(" [%s]" % default_value)
        return default_value

    def run(self):
        if self.required_if is not None and not self.required_if(self.script.options):
            return
        sys.stdout.write(self.message)
        default_value = self.run_default()
        sys.stdout.write('  ')

        value = self.process_value(raw_input())

        if (value is None or str(value).strip() == '') and default_value is not None:
            value = default_value

        self.script.options[self.key] = value

        sys.stdout.write('\n')
        return value

    def process_value(self, value):
        return value

    def get_default(self):
        if inspect.ismethod(self.default) or inspect.isfunction(self.default):
            return self.default(self.script.options)
        return self.default


class BooleanCue(Cue):
    def __init__(self, script, key, message, default, required_if=None):
        super(BooleanCue, self).__init__(script, key, message, default, [True, False], required_if)

    def run_default(self):
        default_value = None
        if self.default is not None:
            default_value = self.get_default()
            options = ['y', 'n']

            if default_value:
                options[0] = options[0].upper()
            else:
                options[1] = options[1].upper()

            sys.stdout.write(" [%s]" % "/".join(options))

    def process_value(self, value):
        return value.lower() == 'y'


class Script(object):
    def __init__(self, name):
        self.name = name
        self.cues = []
        self.options = {}

    def start(self):
        print(self.name)
        for cue in self.cues:
            cue.run()

    def add_cue(self, key, message, default=None, choices=None, required_if=None):
        self.cues.append(Cue(self, key, message, default, choices, required_if=required_if))

    def add_boolean_cue(self, key, message, default=None, required_if=None):
        self.cues.append(BooleanCue(self, key, message, default, required_if=required_if))

    def sluggify(self, value):
        return value.lower().replace(' ', '')


def main(args=None):
    if args is None:
        args = sys.argv[:1]

    script = Script('cow framework application generator')

    script.add_cue('name', 'What\'s the name of your project?')
    script.add_cue('slug', 'What\'s the slug for your project?', default=lambda options: script.sluggify(options['name']))

    script.add_boolean_cue('use_mongodb', 'Are you going to be using MongoDB?', default=False)
    script.add_cue('mongodb_host', 'MongoDB hostname for local development:', required_if=lambda options: options['use_mongodb'])

    script.add_boolean_cue('use_redis', 'Are you going to be using Redis?', default=False)
    script.add_boolean_cue('use_elastic_search', 'Are you going to be using ElasticSearch?', default=False)
    script.add_boolean_cue('use_geocoding', 'Are you going to be using Google Geocoding API?', default=False)

    script.start()

    print script.options

if __name__ == '__main__':
    main()
