#!/usr/bin/python
# coding=utf-8
import pyinotify
import os, glob
import re
import logging
from string import Template

class InactionfileError(Exception): pass

class Rule(object):
    '''A rule bind command to a pathname'''
    def __init__(self, pathname, events, command):
        self.pathname = pathname
        self.events = events
        self.command = command

    def execute(self):
        real_cmd = Template(self.command).substitute({
            'pathname': self.pathname,
            'name': os.path.basename(self.pathname),
            'path': os.path.dirname(self.pathname),
        })

        #如果命令以@开头, 则去掉@, 不输出命令.
        if real_cmd.startswith('@'):
            real_cmd = real_cmd[1:]
        else:
            print real_cmd

        os.system(real_cmd)

    def __repr__(self):
        return 'inaction.Rule("%s", %s, "%s")' % (self.pathname,
                                                  self.events,
                                                  self.command)

class Rules(dict):
    '''rules parsed from Inactionfile'''
    def __init__(self, acfile='Inactionfile'):
        def parse_line(l):
            pathnames,events,command = [ s.strip() for s in re.split('\s+', l, 2) ]

            events = [ pyinotify.EventsCodes.ALL_FLAGS.get(flag.strip())
                     for flag in events.split(',') ]

            if None in events:
                raise InactionfileError('Not recognized event type')

            # support multiple files in one rule
            for pathname in pathnames.split(','):
                for pathname in glob.glob(pathname):
                    # support Unix style pathname pattern expansion in pathname
                    pathname = os.path.realpath(pathname)
                    self[pathname] = Rule(pathname, events, command)

        with open(acfile) as f:
            for l in f:
                l = re.sub('\s*#.*$', '', l).strip()
                if not l:
                    continue
                parse_line(l)

    def related_events(self):
        es = []
        for f,r in self.items():
            es += r.events
        return list(set(es))

class InActionHandler(pyinotify.ProcessEvent):
    def my_init(self):
        pass

    def set_rules(self, rules):
        self.rules = rules

    def process_default(self, event):
        if os.path.basename(event.pathname) == 'Inactionfile':
            print 'reloading Inactionfile...'
            self.set_rules(Rules())

        event_pathname = os.path.realpath(event.pathname)
        rule = self.rules.get(event_pathname)
        if not rule: return
        for expected_event in rule.events:
            if event.mask & expected_event:
                rule.execute()
                logging.debug('Hit %s(mask %s,%s)' % (event_pathname,
                                                     event.maskname,
                                                     event.mask))
                break

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='...')

    parser.add_option("-r", "--recursive", action="store_true",
                      dest="recursive",
                      help="Add watches recursively on paths")
    parser.add_option("-a", "--auto_add", action="store_true",
                      dest="auto_add",
                      help="Automatically add watches on new directories")
    parser.add_option("-C", "--proj_dir", action="store",
                      dest="proj_dir",
                      help="Change to proj_dir before doing anything.")

    (options, args) = parser.parse_args()

    if options.proj_dir:
        print 'chdir from `%s` to `%s`' % (os.getcwd(), options.proj_dir)
        os.chdir(options.proj_dir)


    rules = Rules()
    watching_files = rules.keys()

    mask = reduce(lambda x, y: x | y, rules.related_events())
    wm = pyinotify.WatchManager()

    real_watching_paths = [ os.path.dirname(p) if not os.path.isdir(p) else p for p in watching_files ]
    logging.debug('real_watching_paths: %s' % real_watching_paths)
    wm.add_watch(real_watching_paths,
                 mask,
                 rec=options.recursive,
                 auto_add=options.auto_add,)

    wm.add_watch('Inactionfile',
                 pyinotify.IN_MODIFY | pyinotify.IN_CLOSE_WRITE)

    handler = InActionHandler()
    handler.set_rules(rules)

    notifier = pyinotify.Notifier(wm, handler)
    print "Start monitoring on:\n", '\n'.join(watching_files)
    notifier.loop()
