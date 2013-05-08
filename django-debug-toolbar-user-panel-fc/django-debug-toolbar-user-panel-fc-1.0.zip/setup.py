#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-debug-toolbar-user-panel-fc',
    description="Panel for the Django Debug toolbar to quickly switch between users.",
    version='1.0',
    url='https://github.com/futurecolors/django-debug-toolbar-user-panel',

    author='Playfire.com',
    author_email='tech@playfire.com',
    license='BSD',

    packages=(
        'debug_toolbar_user_panel',
    ),
    package_data={'': [
        'templates/debug_toolbar_user_panel/*',
    ]},
)
