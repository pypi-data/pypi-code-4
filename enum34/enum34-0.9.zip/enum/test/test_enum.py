import sys

sys.path.insert(0, '../..')
pyver = float('%s.%s' % sys.version_info[:2])

if pyver < 3:
    from py2_test_enum import *
else:
    from py3_test_enum import *

if __name__ == '__main__':
    unittest.main()
