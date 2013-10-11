#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    keen importer: setup script

    :author: Sam Gammon <sam@keen.io>
    :license: This software follows the MIT (OSI-approved)
              license for open source software. A truncated
              version is included here; for full licensing
              details, see ``LICENSE.md`` in the root directory
              of the project.

              Copyright (c) 2013, Keen IO

              The above copyright notice and this permission notice shall be included in
              all copies or substantial portions of the Software.

              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
              THE SOFTWARE.

'''

# distutils
from setuptools import setup


setup(name="importer",
      version="1.1",
      description="Data transfer tool for analytics providers",
      author="Sam Gammon",
      scripts=["bin/importer"],
      author_email="sam@keen.io",
      url="https://github.com/keenlabs/Keen-Importer",
      packages=["importer", "importer_tests", "importer.lib.mixpanel"],
      install_requires=["keen", "pytz"],
      tests_require=["nose"]
)
