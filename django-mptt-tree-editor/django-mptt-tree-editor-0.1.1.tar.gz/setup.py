from setuptools import setup, find_packages

setup(
    name = "django-mptt-tree-editor",
    version = "0.1.1",
    packages = find_packages(),
    author = "Santiago Piccinini",
    author_email = "spiccinini@codigosur.org",
    description = "Provides FeinCMS's mptt admin tree editor as a separate app",
    license='BSD License',
    platforms=['OS Independent'],
    url = "http://bitbucket.org/san/django-mptt-tree-editor",
    include_package_data = True,
    install_requires=[
        'Django>=1.4',
        'django-mptt>=0.4',
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
    ],
)
