# installation:
#  * pip install virt-back
#  * easy_install virt-back
from setuptools import setup

DESCRIPTION = """A backup utility for QEMU, KVM, XEN, and Virtualbox guests.
Virt-back is a python application that uses the libvirt api to safely 
shutdown, gzip, and restart guests.  The backup process logs to syslog
for auditing and virt-back works great with cron for scheduling outages.
Virt-back has been placed in the public domain and 
the latest version may be downloaded here:
https://bitbucket.org/russellballestrini/virt-back
"""

setup( 
    name = 'virt-back',
    version = '0.1.0',
    description = 'virt-back: A backup utility for QEMU, KVM, XEN, and Virtualbox guests',
    keywords = 'backup virtual hypervisor QEMU KVM XEN Virtualbox',
    long_description = DESCRIPTION,

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/virt-back',

    platforms = ['All'],
    license = 'Public Domain',

    py_modules = ['virtback'],
    include_package_data = True,

    scripts=['virt-back'],
)

"""
setup()
  keyword args: http://peak.telecommunity.com/DevCenter/setuptools

configure pypi username and password in ~/.pypirc::

 [pypi]
 username:
 password:


build and upload to pypi with this::

 python setup.py sdist bdist_egg register upload
"""
