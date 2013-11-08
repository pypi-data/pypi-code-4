from setuptools import setup, find_packages
from django_queue_mailer import VERSION


setup(
    name='django_queue_mailer',
    version=VERSION,
    description="A reusable Django app for controlling queuing and sending of app emails",
    long_description=open('README.rst').read(),
    keywords='django_queue_mailer',
    author='Eduard Kracmar',
    author_email="info@adaptiware.com",
    url='https://bitbucket.org/edke/django-queue-mailer',
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications :: Email",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Utilities",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    include_package_data=True
)
