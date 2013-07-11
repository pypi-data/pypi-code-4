# This is a module

__version__ = "1.3"

def funchello():
    print "Hello world from file '%s'" % __file__
    print "This is version '%s'" % __version__

if __name__ == '__main__':
    # A simple file test
    funchello()
