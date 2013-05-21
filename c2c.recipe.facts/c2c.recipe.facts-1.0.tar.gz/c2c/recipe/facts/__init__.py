# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
from os import environ
import yaml


class Facts(object):

    def __init__(self, buildout, name, options):
        env = environ
        if 'PATH' not in env:
            env = env.copy()
            env['PATH'] = '/usr/bin:/bin'

        p = Popen(['facter', '-y'], stdout=PIPE, env=env)
        p.wait()
        y = yaml.load(p.stdout.read())
        for k in y:
            options[k] = str(y[k])

    def install(self):
        return ()

    update = install
