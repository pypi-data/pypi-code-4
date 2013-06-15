import os
from subprocess import Popen, PIPE
from inkwave.core import Transform


class Sass(Transform):
    def __init__(self, *args, scss=False, style='compact', **kwargs):
        super(Sass, self).__init__(*args, **kwargs)
        self.scss = scss
        self.style = style
        self.cmd = ['sass', '-s']
        self.cmd += ['-t', style]

    def init(self, env):
        super(Sass, self).init(env)
        self.cmd += ['--cache-location',
                     os.path.join(env.cache_path, 'sass')]

    def transform(self):
        try:
            for d in self.source.all():
                cmd = self.cmd
                if 'file_dirname' in d:
                    cmd += ['-I', d['file_dirname']]

                try:
                    if d['file']['ext'] == '.scss' or self.scss:
                        cmd.append('--scss')
                except KeyError:
                    pass

                with Popen(cmd, bufsize=-1,
                           stdin=PIPE, stdout=PIPE) as proc:
                    out, errs = proc.communicate(d['content'])
                    if errs:
                        raise RuntimeError(errs)

                    d['content'] = out
                yield d
        except FileNotFoundError as e:
            raise e
