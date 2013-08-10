from __future__ import absolute_import


class Command(object):
    
    @classmethod
    def run(cls, args=None):
        cmd = cls()
        cmd.start(args)

    @classmethod
    def start(cls, args):
        pass