#!/usr/bin/env python
import sys, os

try:
    from io import open
except ImportError:
    pass

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "\n"+read('docs/index.rst')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)

### Package version number
version = '0.4.9'

setup(
    name="libauthkit",
    version=version,
    description='An extensible authentication and authorization framework on top of WSGI',
    long_description=long_description,
    license = 'ISC',
    maintainer='Etienne Robillard',
    maintainer_email='erob@gthcfoundation.org',
    url='http://www.notmm.org/',
    packages=find_packages(exclude=['test', 'examples', 'docs']),
    include_package_data=True,
    zip_safe=False,
    test_suite = 'nose.collector',
    install_requires = [
        "Paste>=1.7.4", "nose>=0.9.2", "PasteDeploy>=1.1", "Beaker>=1.1",
        "PasteScript>=1.1", "python-openid>=2.1.1", 
        "elementtree>=1.2,<=1.3", "decorator>=2.1.0",
        "WebOb>=0.9.8",
    ],
    extras_require = {
        'pylons': ["Pylons>=0.9.5,<=1.0"],
        'full': [
            "Pylons>=0.9.5,<=1.0", 
            "SQLAlchemy>=0.5.0,<=0.5.99", 
            "pudge==0.1.3", 
            "buildutils==dev", 
            "pygments>=0.7", 
            "TurboKid==0.9.5"
        ],
        'pudge': [
            "pudge==0.1.3", 
            "buildutils==dev", 
            "pygments>=0.7", 
            "TurboKid==0.9.5"
        ],
    },
    entry_points="""
        [authkit.method]
        basic=authkit.authenticate.basic:make_basic_handler
        digest=authkit.authenticate.digest:make_digest_handler
        form=authkit.authenticate.form:make_form_handler
        forward=authkit.authenticate.forward:make_forward_handler
        openid=authkit.authenticate.open_id:make_passurl_handler
        redirect=authkit.authenticate.redirect:make_redirect_handler
        cookie=authkit.authenticate.cookie:make_cookie_handler
        
        cas = authkit.authenticate.sso.cas:make_cas_handler

        [paste.paster_create_template]
        authenticate_plugin=authkit.template:AuthenticatePlugin
    """,
)
