import pkg_resources

def get_version():
    fname = pkg_resources.resource_filename('vr.runners', 'version.txt')
    with open(fname, 'rb') as f:
        return f.readline()
