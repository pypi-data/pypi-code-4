import sys

OSX = 'osx'
LINUX = 'linux'


def get_platform():
    platform = sys.platform.lower()
    if 'darwin' in platform:
        return OSX
    elif 'linux' in platform:
        return LINUX
    raise RuntimeError("Platform %r is not supported, sorry" % platform)

PLATFORM = get_platform()

