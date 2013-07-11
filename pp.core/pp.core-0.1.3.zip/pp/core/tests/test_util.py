# -*- encoding=utf-8 -*-

################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
from pp.core import util 

def test_check_commmand():
    assert util.check_command('ls') == True
    assert util.check_command('foo') == False

def test_runcmd_existing_command():
    result = util.run_cmd('ls /tmp')
    assert result['status'] ==  0

def test_runcmd_non_existing_command():
    result = util.run_cmd('does.not.exist /tmp')
    assert result['status'] != 0

def test_slugify():
    assert util.slugify(u'Ein schönes Projekt') == 'ein-schones-projekt'

def test_safe_unlink():
    import tempfile

    tempdir = tempfile.mktemp()
    util.safe_unlink(tempdir)
    assert os.path.exists(tempdir) == False
