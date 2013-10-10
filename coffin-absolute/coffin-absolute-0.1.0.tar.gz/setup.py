from setuptools import setup

DESCRIPTION = "Provides absolute_url tag and filter in Jinja2 templates when using the coffin package with Django."
LONG_DESCRIPTION = open('README.rst').read()

setup(
        name='coffin-absolute',
        version=__import__('coffin_absolute').__version__,
        packages=['coffin_absolute'],
        author='Nikolay Zalutskiy',
        author_email='pacemkr@{nospam}gmail.com',
        url='https://github.com/pacemkr/coffin-absolute',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        classifiers=[
            "Framework :: Django",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Environment :: Web Environment",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        )
