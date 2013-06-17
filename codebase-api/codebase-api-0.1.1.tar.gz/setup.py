from setuptools import setup


setup(
    name="codebase-api",
    version="0.1.1",
    author="Pablo Recio",
    author_email="pablo@recio.me",
    description="Wrapper library for connecting with CasebaseHQ API",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    license="BSD",
    keywords="codebase api wrapper",
    url='https://github.com/pyriku/codebase-python',
    packages=['codebase'],
    install_requires=[
        'requests',
    ],
)
