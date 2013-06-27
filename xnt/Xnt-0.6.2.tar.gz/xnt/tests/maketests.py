#!/usr/bin/env python
"""Make (make/ant/nant) Tests Module"""

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

import unittest
import xnt
import xnt.build.make
import xnt.tests

@unittest.skipUnless(xnt.in_path("ant") or xnt.in_path("ant.exe"),
                     "Apache ant is not in your path")
class AntTests(unittest.TestCase):
    """Test Case for Ant Build"""
    def setUp(self):
        """Test Setup"""
        xnt.tests.set_up()
        with open("temp/build.xml", "w") as build:
            build.write("<?xml version=\"1.0\" ?>\n")
            build.write("<project name=\"test\" default=\"test\">\n")
            build.write("<target name=\"test\">\n")
            build.write("<echo>${test_var}</echo>\n")
            build.write("</target>\n")
            build.write("</project>\n")

    def tearDown(self):
        """Test Teardown"""
        xnt.tests.tear_down()

    def test_default_build(self):
        """Test the default target of ant"""
        result = xnt.build.make.ant(target="test", path="temp")
        self.assertEqual(result, 0)

    def test_passing_flags(self):
        """Test ant with passing flags"""
        result = xnt.build.make.ant(target="test",
                                    path="temp",
                                    flags=["-verbose"])
        self.assertEqual(result, 0)

    def test_pass_var(self):
        """Test passing variables to ant"""
        result = xnt.build.make.ant(target="test", path="temp",
                                    pkeys=["test_var"],
                                    pvalues=["testing"])
        self.assertEqual(result, 0)

@unittest.skipUnless(xnt.in_path("make"), "make is not in your path")
class MakeTests(unittest.TestCase):
    """GNU Make Tests"""

    def setUp(self):
        """Test Setup"""
        xnt.tests.set_up()
        with open("temp/Makefile", "w") as makefile:
            makefile.write("build:\n")
            makefile.write("\techo 'testing'\n")

    def tearDown(self):
        """Test Teardown"""
        xnt.tests.tear_down()

    def test_default_make(self):
        """Test Default make"""
        result = xnt.build.make.make(target="build", path="temp")
        self.assertEqual(result, 0)

    def test_passing_vars(self):
        """Test Parameter Passing with Make"""
        result = xnt.build.make.make(target="build",
                                     path="temp",
                                     pkeys=["test_var"],
                                     pvalues=["testing"])
        self.assertEqual(result, 0)

    def test_passing_flags(self):
        """Test Flag Passing with Make"""
        result = xnt.build.make.make(target="build",
                                     path="temp",
                                     flags=["-B"])
        self.assertEqual(result, 0)

@unittest.skipUnless(xnt.in_path("nant") or xnt.in_path("nant.exe"),
                     "nant is not in your path")
class NAntTests(unittest.TestCase):
    """.NET Ant Tests"""

    def setUp(self):
        """Test Setup"""
        xnt.tests.set_up()
        with open("temp/default.build", "w") as default_build:
            default_build.write("<?xml version=\"1.0\"?>\n")
            default_build.write("<project name=\"test\">\n")
            default_build.write("<target name=\"test\">\n")
            default_build.write("<if \n")
            default_build.write("test=\"${property::exists('test_var')}\">\n")
            default_build.write("<echo>${test_var}</echo>\n")
            default_build.write("</if>\n")
            default_build.write("</target>\n")
            default_build.write("</project>")

    def tearDown(self):
        """Test Teardown"""
        xnt.tests.tear_down()

    def test_default_nant(self):
        """Test Deault nant"""
        result = xnt.build.make.nant(target="test", path="temp")
        self.assertEqual(result, 0)

    def test_parameters_passing(self):
        """Test Parameter Passing with NAnt"""
        result = xnt.build.make.nant(target="test",
                                     path="temp",
                                     pkeys=["test_var"],
                                     pvalues=["testing"])
        self.assertEqual(result, 0)

    def test_flag_passing(self):
        """Test Flag Passing with NAnt"""
        result = xnt.build.make.nant(target="test",
                                     path="temp",
                                     flags=["-v"])
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
