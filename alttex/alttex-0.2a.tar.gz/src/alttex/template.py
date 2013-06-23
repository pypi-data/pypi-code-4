import os
import jinja2
from .util import escape_tex, env_partition, env_content, readfile

class Template:
    JINJA_ENV = jinja2.Environment(
        block_start_string='\CMD{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\CMT{',
        comment_end_string='}',
        line_statement_prefix='%-',
        line_comment_prefix='%!',
        trim_blocks=True,
        autoescape=False,
    )
    JINJA_ENV.filters['escape'] = escape_tex

    def __init__(self, source, filename=None):
        self.source, self.filename = readfile(source, None)
        if filename is not None:
            self.filename = filename
        self.has_jinja = False

        # Search for \begin{DATA} blocks
        self._datablock = None
        if r'\begin{DATA}' in self.source:
            pre, env, post = env_partition(source, 'DATA')
            self.template_source = pre + post
            env_data, args = env_content(env)
            data_t = args.pop()
            self._dataiter = getattr(self, '_data_iter_%s' % data_t)(env_data, *args)

        # Search for \DATASOURCE[data type]{fname} commands
        elif r'\DATASOURCE' in self.source:
            raise NotImplementedError()

        # Search for files with data content
        else:
            self.template_source = self.source
            name = os.path.splitext(self.filename)[0]
            files = os.listdir(os.getcwd())
            files = [ f for f in files if f.startswith(name) ]

            # Choose the best data source file
            for f in files:
                name, ext = os.path.splitext(f)
                for tt in ('.json', '.py'):
                    if ext == tt:
                        dataiter = getattr(self, '_data_iter_%s' % tt[1:])
                        self._dataiter = dataiter(self.template_source)
                        break
                else:
                    continue
                break

            # If no suitable file was found, use an empty one  
            if not hasattr(self, '_dataiter'):
                self._dataiter = self._data_iter_empty(self.template_source)


        # Check if source has any Jinja hooks
        for cmd in r'\VAR \CMD \CMT %- %!'.split():
            if cmd in self.template_source:
                self.has_jinja = True
                break
        if self.has_jinja:
            self.template = self.JINJA_ENV.from_string(self.template_source)

    # Data sources -------------------------------------------------------------
    def _data_iter_empty(self, src=None, opt=None):
        'Create empty data dictionaries (for documents without DATA sources)'
        while True:
            yield {}

    def _data_iter_py(self, src, opt=None):
        'Data source is a python script'
        code = compile(src, '<string>', 'exec')
        while True:
            namespace = {}
            exec(code, namespace)
            yield namespace

    # Other --------------------------------------------------------------------
    def render(self, data=None):
        '''Renders document using the default data source or the given 
        dictionary `data`.'''

        if not self.has_jinja:
            return self.template_source
        else:
            if data is None:
                data = next(self._dataiter)
            return self.template.render(data)


if __name__ == '__main__':
    txt = r'''\documentclass{article}
\begin{DATA}{python}
import random
foobar = random.randrange(10)
\end{DATA}
\begin{document}
\begin{itemize}
%- for i in range(5)
    \item Hello \VAR{i}!
%- endfor
Foobar: \VAR{foobar}
\end{itemize}
\end{document}
'''
    t = Template(txt)
    print(t.render())

    import doctest
    doctest.testmod()
