import os
from alttex.util import readfile, join_tex, JOIN_CLEARPAGE
from alttex.altsource import AltSource
from alttex.template import Template

class Job:
    def __init__(self, file, filename=None):
        self.data, self.filename = readfile(file, filename)
        if self.filename.endswith('.lyx'):
            self.read_lyx()
        self.altsource = AltSource(self.data, self.filename)

        # Private attributes
        self._sections = self.altsource.sections()
        self._output_name = os.path.splitext(self.filename)[0]
        self._exts = []
        self._texfiles = set()

    def set_sections(self, sections):
        '''Set the sections that shall be used in the final document'''
        self._sections = list(sections)

    def set_output(self, output_name):
        '''Sets the name for the output file'''
        name, ext = os.path.splitext(output_name)
        self._output_name = name
        self._exts.append(ext[1:])

    def read_lyx(self):
        os.system('lyx -e latex %s' % self.filename)
        filename = self.filename[:-4] + '.tex'
        self.data, self.filename = readfile(open(filename), filename)

    #===========================================================================
    # Make final documents
    #===========================================================================
    def make_final(self):
        exts = self._exts or ['pdf']
        for ext in exts:
            worker = getattr(self, 'make_' + ext)
            worker()

    def make_pdf(self):
        self.make_tex()
        for f in self._texfiles:
            os.system('pdflatex -interaction=nonstopmode %s > /dev/null' % f)

    def make_tex(self):
        for section in self._sections:
            texfile = '%s-%s.tex' % (self._output_name, section)
            sourcefile = self._output_name + '.tex'
            docs = self.altsource.get_section(section)
            docs = [ Template(doc, sourcefile).render() for doc in docs ]
            data = join_tex(docs, as_document=True, join=JOIN_CLEARPAGE)
            with open(texfile, 'w') as F:
                F.write(data)
                self._texfiles.add(texfile)
