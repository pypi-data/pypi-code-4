import sys
from distutils.version import LooseVersion
req_version = LooseVersion('2.5')
cur_version = LooseVersion('.'.join([str(v) for v in sys.version_info[:3]]))
if cur_version < req_version:
    print "Minimum Python version %s required.  You have %s." % (req_version, cur_version)
    sys.exit(1)
