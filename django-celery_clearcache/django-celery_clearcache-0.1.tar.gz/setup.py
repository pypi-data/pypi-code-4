import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-celery_clearcache',
    version='0.1',
    packages=['celery_clearcache'],
    include_package_data=True,
    license='GPLv3 License',
    description='Clear cached stale sessions with celery task',
    long_description=README,
    url='http://v.licheni.net/drc/django-celer_clearcache.git',
    author='Davide Riccardo Caliendo',
    author_email='davide.licheni.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

