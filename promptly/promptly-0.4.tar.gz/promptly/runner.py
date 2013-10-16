# -*- coding: utf-8 -*-
import sys
import signal
import pkg_resources
from .styles import CSSParser
from .compat import iterkeys, input


class BaseRunner(object):

    def __init__(self, prefix=None, stylesheet=None):
        self.prefix = prefix
        self.stylesheet = stylesheet
        signal.signal(signal.SIGINT, self._on_sigint)

    # signal handlers
    def _on_sigint(self, signal, frame):
        print('You Quit! You\'re a quitter! Boo!')
        sys.exit(0)

    def goto(self, key):
        form = self.form
        keys = list(iterkeys(form._fields))

        try:
            index = keys.index(key)
        except ValueError:
            return

        self._sequence = (x for i, x in enumerate(keys) if i > index)

    def info(self, value):
        pass

    def error(self, value):
        pass

    def __call__(self, form):

        self._sequence = iterkeys(form._fields)

        self.form = form
        prefix = '' if not self.prefix else self.prefix

        if self.stylesheet:
            styles = CSSParser.parse_string(self.stylesheet)
        else:
            stream = pkg_resources.resource_stream(
                'promptly.resources',
                'default.css'
            )

            styles = CSSParser.parse_string(stream.read())

        for item in self._sequence:
            target = getattr(form, item)

            prompt = target.build_prompt(prefix=prefix,
                                         stylesheet=styles)

            while True:
                data = self.prompt(prompt, target.)

                try:
                    target(data=data, runner=self)
                except ValueError:
                    continue
                break


class ConsoleRunner(BaseRunner):
    def prompt(self, prompt, ):
        # we want a trailing space
        if
        return input('%s ' % prompt)
