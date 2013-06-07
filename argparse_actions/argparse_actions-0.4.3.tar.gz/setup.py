from distutils.core import setup

setup_details = dict(
    name='argparse_actions',
    version='0.4.3',
    author='Hai Vu',
    author_email='haivu2004@gmail.com',
    packages=['argparse_actions', 'argparse_actions.test'],
    url='http://pypi.python.org/pypi/argparse_actions/',
    license='LICENSE.txt',
    description='Custom actions for argparse package',
    long_description=open('README.md').read(),
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
    ]
)

setup(**setup_details)
