import logging
import os
import shutil
import hashlib
from time import perf_counter

from cliff.command import Command
from inkwave.core import env


class Skip(Exception):
    pass


def digest(path):
    with open(path, 'rb') as fd:
        return hashlib.sha1(fd.read())


class Build(Command):
    "Build website"

    site = True
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Build, self).get_parser(prog_name)
        parser.add_argument('--clean',
                            action='store_true',
                            help='Clean up the build directory')
        parser.add_argument('--force',
                            action='store_true',
                            help='Force rebuild')
        parser.add_argument('resource',
                            nargs='?',
                            help='Resource to build')
        return parser

    def _build(self, res, index, force):
        self.log.info('Building resource: {}'.format(res.name))

        t1 = perf_counter()
        for result in res.all():
            try:
                state = 'OK'
                out_path = os.path.join(env.out, path)
                try:
                    os.makedirs(os.path.dirname(out_path))
                except FileExistsError:
                    pass

                if not force and os.path.exists(out_path):
                    if digest(out_path) == content.digest():
                        raise Skip()

                with open(out_path, 'wb+') as fd:
                    fd.write(bytes(content))
            except Skip:
                state = 'SKIP'
            except Exception as e:
                state = 'FAIL'
                if self.app.options.debug:
                    self.log.exception(e)
                else:
                    self.log.error(e)

            index.add(path)
            t2 = perf_counter()
            self.log.info(' - ({:f} sec) {} [{}]'.format(t2-t1,
                                                         path,
                                                         state))
            t1 = t2

    def take_action(self, args):
        env.init_db()

        index = set()

        if args.clean:
            shutil.rmtree(env.out)

        if args.resource:
            if args.resource in env.resources:
                self._build(env.resources[args.resource],
                            index, args.force)
            else:
                self.app.stdout.write('Resource "{}" is not'
                                      ' found\n'.format(args.resource))
        else:
            for res in env.resources.routes:
                t1 = perf_counter()

                for url in res.all():
                    state = 'OK'
                    out_path = os.path.join(env.out, url[1:])
                    if out_path[-1] == '/' or out_path == env.out:
                        out_path = os.path.join(out_path, 'index.html')
                    if res.ext:
                        out_path += res.ext

                    try:
                        os.makedirs(os.path.dirname(out_path))
                    except FileExistsError:
                        pass
                    content_type, encoding, content = \
                        env.resources.dispatch('get', url)
                    with open(out_path, 'wb+') as fd:
                        if isinstance(content, str):
                            fd.write(bytes(content, encoding))
                        else:
                            fd.write(content)
                    t2 = perf_counter()
                    self.app.stdout.write(' [{:^4}] ({:.4f}) {}\n'
                                          .format(state, t2-t1, out_path))
                    t1 = t2
