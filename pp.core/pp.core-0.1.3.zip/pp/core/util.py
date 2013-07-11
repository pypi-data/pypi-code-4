################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import re
import time
import shutil
import subprocess
from unicodedata import normalize
from pp.core.logger import LOG

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def run_cmd(cmd):
    """ Execute a command using the subprocess module """
    ts = time.time()
    LOG.debug('Running %s' % cmd)
    stdin = open('/dev/null')
    stderr = stdout = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)  
    status = p.wait()
    duration = time.time() - ts
    LOG.debug('Exit code: %d, duration: %2.3f seconds' % (status, duration))
    return dict(status=status,
                duration=duration,
                stderr=p.stderr.read().strip(),
                stdout=p.stdout.read().strip())


def check_command(cmd):
    """ Check if 'cmd' exists within $PATH """
    path = os.environ.get('PATH')
    if path is None:
        raise ValueError('$PATH not set')
    for dir in path.split(':'):
        if os.path.exists(os.path.join(dir, cmd)):
            return True
    return False


def safe_unlink(file_or_directory):
    """ Safe removal of a file or directory """
    if not os.path.exists(file_or_directory):
        return
    if os.path.isfile(file_or_directory):
        os.unlink(file_or_directory)
    else:
        shutil.rmtree(file_or_directory)
