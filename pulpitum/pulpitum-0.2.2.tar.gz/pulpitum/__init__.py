try:
    from .api import PyPI
    from .package import Package
    from . import tests
    from . import errors
except:
    pass

__version__ = "0.2.2"
