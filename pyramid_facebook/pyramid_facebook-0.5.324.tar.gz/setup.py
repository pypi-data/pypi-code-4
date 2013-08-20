# -*- coding: utf-8 -*-
import setuptools

# this mixes setup deps with test deps, but our internal test tool
# (based on nosetests) was not working properly with test deps
setup_requires = [
    'd2to1',
]

setuptools.setup(
    setup_requires=setup_requires,
    d2to1=True,
    test_suite='nose.collector',
    entry_points="""
        [console_scripts]

        pfacebook-real-time=pyramid_facebook.real_time:command_line_script
    """
)
