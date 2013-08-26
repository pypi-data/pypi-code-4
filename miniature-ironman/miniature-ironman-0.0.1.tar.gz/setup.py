import os
from setuptools import setup
from miniature import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='miniature-ironman',
    version=".".join(map(str, VERSION)),
    description='My code snippets set for django',
    long_description=readme,
    author="Ilya Beda",
    author_email='ir4y.ix@gmail.com',
    url='https://github.com/ir4y/miniature-ironman',
    packages=['miniature'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    classifiers=[
    'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
