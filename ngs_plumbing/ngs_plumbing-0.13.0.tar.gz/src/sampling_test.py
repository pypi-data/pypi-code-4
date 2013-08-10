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
from ngs_plumbing import sampling

if sys.version_info[0] == 2:
    _is_python3 = False
else:
    _is_python3 = True


def itemkey(x):
    if _is_python3:
        res = ascii(x)
        res = res.encode('ASCII')
    else:
        res = str(x)
    return res

class SamplingTestCase(unittest.TestCase):

    def test_ReservoirSample(self):
        data = (1,2,3)
        spl = sampling.ReservoirSample(3)
        for item in data:
            spl.add(item)
        self.assertEquals(3, len(spl))

        data = (1,2,3,4,5)
        spl = sampling.ReservoirSample(3)
        for item in data:
            spl.add(item)
        self.assertEquals(3, len(spl))

    def test_ReservoirSampleBloom(self):
        data = (1,2,3)
        spl = sampling.ReservoirSampleBloom(3, itemkey = itemkey)
        for item in data:
            spl.add(item)
        self.assertEquals(3, len(spl))

        data = (1,2,3,4,5)
        spl = sampling.ReservoirSampleBloom(3, itemkey = itemkey)
        for item in data:
            spl.add(item)
        self.assertEquals(3, len(spl))

        data = (1,2,1)
        spl = sampling.ReservoirSampleBloom(3, itemkey = itemkey)
        for item in data:
            spl.add(item)
        self.assertEquals(2, len(spl))

        

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SamplingTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

