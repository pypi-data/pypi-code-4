from setuptools import setup

setup(
    setup_requires=['d2to1'],
    d2to1=True,
    entry_points="""
        [paste.app_factory]
        main = pyramid_restlogging:main
    """
)
