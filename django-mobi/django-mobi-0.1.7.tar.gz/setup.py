from distutils.core import setup

setup(
    name='django-mobi',
    version='0.1.7',
    description='Django middleware and view decorator to detect phones and small-screen devices',
    maintainer='Ken Cochrane',
    maintainer_email='KenCochrane@gmail.com',
    url='https://bitbucket.org/kencochrane/django-mobi/',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=['mobi',],
    package_data={'mobi': ['*.txt',]},
    long_description=open('README').read(),
)