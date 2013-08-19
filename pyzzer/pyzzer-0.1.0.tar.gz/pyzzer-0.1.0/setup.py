from distutils.core import setup
import sys

sys.path.insert(0, 'pyzzer.pyz')

import pyzzer

setup(
    name='pyzzer',
    description='A tool for creating Python-executable archives.',
    version=pyzzer.__version__,
    license='MIT',
    author='Vinay Sajip',
    author_email='vinay_sajip@yahoo.co.uk',
    maintainer='Vinay Sajip',
    maintainer_email='vinay_sajip@yahoo.co.uk',
    download_url=('http://pypi.python.org/packages/source/p/pyzzer/'
                  'pyzzer-%s.tar.gz' % pyzzer.__version__),
    keywords=['executable', 'archive', 'zip'],
    platforms=['Any'],
    scripts=['pyzzer.pyz', 'pyzzerw.pyz'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: Utilities',
    ],
)
