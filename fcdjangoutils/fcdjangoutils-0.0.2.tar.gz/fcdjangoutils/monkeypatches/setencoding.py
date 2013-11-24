# -*- coding: utf-8 -*-
import sys
reload(sys)
import codecs

sys.setdefaultencoding('UTF-8')
sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
