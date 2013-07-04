# This file is part of ngs_plumbing.

# ngs_plumbing is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ngs_plumbing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import sys, os, tempfile
import io, gzip
from ngs_plumbing.dna import PackedDNABytes
import ngs_plumbing.parsing as parsing
import ngs_plumbing

if sys.version_info[0] == 2:
    _is_python2 = True
else:
    _is_python2 = False

builtins = __builtins__

class ParsingTestCase(unittest.TestCase):

    def setUp(self):
        data_dir = os.path.join(os.path.dirname(ngs_plumbing.__file__), 'data')
        self.filename_fq = os.path.join(data_dir, 'reads.fq')
        self.data_dir = data_dir

    def test_open(self):
        # FASTQ
        rh = parsing.open(self.filename_fq)
        e = next(rh)
        self.assertTrue(hasattr(e, 'sequence'))
        # FASTQ.gz
        rh = parsing.open(self.filename_fq+'.gz')
        e_gz = next(rh)
        self.assertEquals(e.sequence, e_gz.sequence)
        # FASTQ.bz2
        rh = parsing.open(self.filename_fq+'.bz2')
        e_bz2 = next(rh)
        self.assertEquals(e.sequence, e_bz2.sequence)
        

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ParsingTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

