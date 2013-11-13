"Point website users at configurable on-call administrators"

import codecs as _codecs
from distutils.core import setup
import os.path as _os_path

from django_on_call import __version__


_this_dir = _os_path.dirname(__file__)

setup(
    name='django-on-call',
    version=__version__,
    maintainer='W. Trevor King',
    maintainer_email='wking@tremily.us',
    url='https://github.com/wking/django-on-call',
    download_url='https://github.com/wking/django-on-call/archive/v{}.tar.gz'.format(__version__),
    license='BSD License',
    platforms=['all'],
    description=__doc__,
    long_description=_codecs.open(
        _os_path.join(_this_dir, 'README'), 'r', encoding='utf-8').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    packages=['django_on_call'],
    provides=['django_on_call'],
    package_data={'django_on_call': ['templates/django_on_call/*.html']},
    )
