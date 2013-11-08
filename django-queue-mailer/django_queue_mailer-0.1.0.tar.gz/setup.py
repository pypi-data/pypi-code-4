import os
from setuptools import setup, find_packages
from django_queue_mailer import VERSION


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django_queue_mailer',
    version=VERSION,
    description="A reusable Django app for controlling queuing and sending of app emails",
    long_description=
    """
    A reusable Django app for controlling queuing and sending of app emails. Key use case is to move sending of emails
    out of requests to speed-up request time and help to solve problems with sending email, handling deferring of email
    and logging of app email communication.
    """,
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
)
