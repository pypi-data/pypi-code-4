#!/usr/bin/env python

from setuptools import setup


setup(name='mapclient',
     version='0.10.1',
     description='A framework for managing and sharing workflows.',
     author='MAP Client Developers',
     author_email='mapclient-devs@physiomeproject.org',
     url='https://launchpad.net/mapclient',
     packages=['mapclient.core', 'mapclient.mountpoints', 'mapclient.settings', 'mapclient.tools', 'mapclient.tools.annotation', 'mapclient.tools.pluginwizard', 'mapclient.tools.pmr', 'mapclient.tools.pmr.jsonclient', 'mapclient.widgets'],
     package_dir={'mapclient': 'src'},
     package_data={'mapclient.tools.annotation': ['annotation.voc']},
     py_modules=['mapclient.mapclient'],
     entry_points={'console_scripts':['mapclient=mapclient.mapclient:winmain']},
     install_requires=['PySide', 'requests', 'oauthlib'],
)
