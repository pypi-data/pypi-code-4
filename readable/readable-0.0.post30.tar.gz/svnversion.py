
from subprocess import check_output, CalledProcessError

# Script to get subversion revision. Replaces tag_svn_revision froms setuptools,
# which is not PEP386 compatible


def add_revision(version):
    # Read in the version that's currently in RELEASE-VERSION.
    release_version = read_release_version()
    try:
        svninfo = check_output(['svn', 'info'])
    except Exception:
        svninfo = None
    if svninfo:
        svninfodict = _textToDict(svninfo)
        revision = int(svninfodict['Revision'])
        version = '{0}.post{1}'.format(version,revision)
    else:
        version = release_version
    if version != release_version:
        write_release_version(version)
    return version

def _textToDict(shellOutput):
    properties = dict()
    for line in str(shellOutput, encoding='utf8').split('\n'):
        splitLine = line.split(': ')
        if len(splitLine) == 2:
            properties[splitLine[0]] = splitLine[1]
    return properties


def read_release_version():
    try:
        f = open("RELEASE-VERSION", "r")

        try:
            version = f.readlines()[0]
            return version.strip()

        finally:
            f.close()

    except:
        return None


def write_release_version(version):
    f = open("RELEASE-VERSION", "w")
    f.write("%s\n" % version)
    f.close()
