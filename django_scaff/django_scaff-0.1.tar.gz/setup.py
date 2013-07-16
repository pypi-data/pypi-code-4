from distutils.core import setup

setup(
    name="django_scaff",
    version="0.1",
    description="Scaffold creator for Django 1.5+ projects",
    long_description="Please see the Github page for details: http://github.com/juliosmelo/django-scaffold",
    author="Julio Siveira Melo",
    author_email="juliocsmelo@gmail.com",
    url="https://github.com/juliosmelo/django_scaffold/",
    packages=[
        "management",
        "management.commands",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
