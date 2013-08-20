from distutils.core import setup
from setuptools import find_packages
from cron_monitor import __version__ as version

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="django-cron-monitor",
    version=version,
    author="Alex Irpan",
    author_email="alexirpan@berkeley.edu",
    packages=find_packages(),
    include_package_data=True,
    url="http://pypi.python.org/pypi/django-cron-monitor/",
    license="LICENSE.TXT",
    description="Cron monitor script and dashboard",
    long_description=open("README.txt").read(),
    install_requires=required,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points="""
        [console_scripts]
        monitor = cron_monitor.monitor:main
    """
)
