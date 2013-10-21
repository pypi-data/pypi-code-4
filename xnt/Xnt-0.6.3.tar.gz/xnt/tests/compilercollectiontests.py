#!/usr/bin/env python
"""Test Common Compiler Collection"""

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
import shutil
import xnt
import xnt.build.cc as cc
import unittest

#pylint: disable-msg=C0103
@unittest.skipUnless(xnt.in_path("gcc"), "gcc is not in your path")
class GccTests(unittest.TestCase):
    """Test GCC"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.c", "w") as test_code:
            test_code.write("""
            #include <stdio.h>
            int main() {
                printf("Hello, World!\\n");
                return 0;
            }
            """)

    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_gcc(self):
        """Test Default GCC"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.gcc("hello.c")
        self.assertTrue(os.path.isfile("a.out"))
        os.chdir(cwd)

    def test_gcc_o(self):
        """Test GCC with output"""
        cc.gcc_o("temp/hello.c", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(xnt.in_path("g++"), "g++ is not in your path")
class GppTests(unittest.TestCase):
    """Test G++ (C++ GCC)"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.cpp", "w") as test_code:
            test_code.write("""
            #include <iostream>
            int main() {
                std::cout << "Hello, World!" << std::endl;
                return 0;
            }
            """)

    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_gpp(self):
        """Test Default G++"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.gpp("hello.cpp")
        self.assertTrue("a.out")
        os.chdir(cwd)

    def test_gpp_o(self):
        """Test G++ with output"""
        cc.gpp_o("temp/hello.cpp", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(xnt.in_path('nvcc'), 'nvcc is not in your path')
class NvccTests(unittest.TestCase):
    """Test NVCC"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.cu", "w") as test_code:
            test_code.write("""
            __global__ void kernel(float *x) {
                int idx = blockIdx.x;
                x[idx] = 42;
            }
            int main() {
                int size = sizeof(float) * 128;
                float *x = (float*)malloc(size);
                float *dev_x;
                cudaMalloc((void**)&dev_x, size);
                cudaMemcpy(dev_x, x, size, cudaMemcpyHostToDevice);
                kernel<<<128, 1>>>(dev_x);
                cudaMemcpy(x, dev_x, size, cudaMemcpyDeviceToHost);
                cudaFree(dev_x);
                delete(x);
                x = NULL;
            }""")
    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_nvcc(self):
        """Test Default NVCC"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.nvcc("hello.cu")
        self.assertTrue(os.path.isfile("a.out"))
        os.chdir(cwd)

    def test_nvcc_o(self):
        """Test Named Output NVCC"""
        cc.nvcc_o("temp/hello.cu", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(xnt.in_path("javac"), "javac is not in your path")
class JavacTests(unittest.TestCase):
    """Test Javac"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.java", "w") as test_code:
            test_code.write("""
            class hello {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """)

    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_javac(self):
        """Test Default Javac"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.javac("hello.java")
        self.assertTrue(os.path.isfile("hello.class"))
        os.chdir(cwd)

if __name__ == "__main__":
    unittest.main()
