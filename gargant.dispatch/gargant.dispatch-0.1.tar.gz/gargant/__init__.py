try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

try:
    import modulefinder
except ImportError:
    pass
else:
    for p in __path__:
        modulefinder.AddPackagePath(__name__, p)
