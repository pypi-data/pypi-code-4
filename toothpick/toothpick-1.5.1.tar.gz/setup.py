from distutils.core import setup

setup(
    name='toothpick',
    version='1.5.1',
    packages=['toothpick',],
    license='BSD',
    long_description=open('README.markdown').read(),
    url='https://github.com/broadinstitute/toothpick',
    author='Andrew Roberts',
    author_email='adroberts@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
    "requests>1.0.0",
    "inflection",
    "werkzeug",
    ],
)

