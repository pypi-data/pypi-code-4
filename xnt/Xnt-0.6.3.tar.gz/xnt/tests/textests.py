#!/usr/bin/env python
"""Tex Tests Module"""

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2013  Kenny Ballou

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
import xnt
import xnt.build.tex
import xnt.tests

@unittest.skipUnless(xnt.in_path("pdflatex") or xnt.in_path("pdflatex.exe"),
                     "pdflatex is not in your path")
class TexTests(unittest.TestCase):
    """Test Case for TeX Document Building"""

    def setUp(self):
        """Test Setup"""
        xnt.tests.set_up()
        with open("temp/test.tex", "w") as test_tex:
            test_tex.write('\\documentclass{article}\n')
            test_tex.write('\\usepackage{glossaries}\n')
            test_tex.write('\\author{python test}\n')
            test_tex.write('\\date{\\today}\n')
            test_tex.write('\\makeglossaries\n')
            test_tex.write('\\begin{document}\n')
            test_tex.write('\\nocite{*}\n')
            test_tex.write('\\newglossaryentry{test}\n')
            test_tex.write('{name={test},description={this}}\n')
            test_tex.write('This is a \\gls{test} \\LaTeX document.\n')
            test_tex.write('\\printglossaries\n')
            test_tex.write('\\begin{thebibliography}{1}\n')
            test_tex.write('\\bibitem{test_bib_item}\n')
            test_tex.write('Leslie Lamport,\n')
            test_tex.write('\\emph{\\LaTeX: A Document Preperation System}.\n')
            test_tex.write('Addison Wesley, Massachusetts,\n')
            test_tex.write('2nd Edition,\n')
            test_tex.write('1994.\n')
            test_tex.write('\\end{thebibliography}\n')
            test_tex.write('\\bibliography{1}\n')
            test_tex.write('\\end{document}\n')

    def tearDown(self):
        """Test Teardown"""
        xnt.tests.tear_down()

    def test_pdflatex_build(self):
        """Test default pdflatex build"""
        xnt.build.tex.pdflatex("test.tex",
                               path="temp")
        self.assertTrue(os.path.exists("temp/test.pdf"))
        self.assertTrue(os.path.exists("temp/test.aux"))
        self.assertTrue(os.path.exists("temp/test.log"))

    def test_pdflatex_with_bibtex(self):
        """Test pdflatex with bibtex"""
        xnt.build.tex.pdflatex("test.tex",
                               path="temp",
                               bibtex=True)
        self.assertTrue(os.path.exists("temp/test.pdf"))
        self.assertTrue(os.path.exists("temp/test.bbl"))
        self.assertTrue(os.path.exists("temp/test.blg"))

    def test_pdflatex_with_glossary(self):
        """Test pdflatex with glossary output"""
        xnt.build.tex.pdflatex("test.tex",
                               path="temp",
                               makeglossary=True)
        self.assertTrue(os.path.exists("temp/test.pdf"))
        self.assertTrue(os.path.exists("temp/test.glo"))
        self.assertTrue(os.path.exists("temp/test.glg"))
        self.assertTrue(os.path.exists("temp/test.gls"))

    def test_tex_clean(self):
        """Test the default clean method removes generated files except pdf"""
        xnt.build.tex.pdflatex("test.tex",
                               path="temp",
                               bibtex=True,
                               makeglossary=True)
        xnt.build.tex.clean(path="temp")
        self.assertTrue(os.path.exists("temp/test.pdf"))
        self.assertFalse(os.path.exists("temp/test.aux"))
        self.assertFalse(os.path.exists("temp/test.log"))

    def test_tex_clean_include_pdf(self):
        """Test Clean; including PDF"""
        xnt.build.tex.pdflatex("test.tex",
                               path="temp",
                               bibtex=True,
                               makeglossary=True)
        xnt.build.tex.clean(path="temp", remove_pdf=True)
        self.assertFalse(os.path.exists("temp/test.pdf"))
        self.assertFalse(os.path.exists("temp/test.aux"))
        self.assertFalse(os.path.exists("temp/test.log"))

if __name__ == '__main__':
    unittest.main()
