def extension(buildout):
    import setuptools.ssl_support
    setuptools.ssl_support.is_available = False
