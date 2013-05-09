from distutils.core import setup

setup(
    name = "django-public-holidays",
    version = "0.1.5",
    description = "Reusable public holidays for django projects",
    url = "http://bitbucket.org/schinckel/django-public-holidays/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "public_holidays",
    ],
    package_data = {
        'public_holidays': [
            'fixtures/*.json',
            'templates/public_holidays/*'
        ]
    },
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    install_requires = [
        'django',
        'django-jsonfield',
        'django-countries',
        'django-model-utils',
    ]
)
