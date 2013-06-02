from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='dynComLogin',
      version=version,
      description="log in to dyn.com",
      long_description="""\
Prevent account expiration by automatically logging in to dyn.com.

Did you get the friendly "Starting now, if you would like to maintain your
free Dyn account, you must log into your account once a month" email from
dyn.com? Then just have this script executed eg. by cron at least once per
month.

Usage: python -m dynComLogin [options]

Options:
  -h, --help            show this help message and exit

  Mandatory 'Options':
    These 'options' must be given.

    -l LOGIN, --login=LOGIN
                        your dyn.com login. Default: Environment variable
                        DYN_COM_LOGIN
    -p PASSWD, --password=PASSWD
                        your dyn.com password. Default: Environment variable
                        DYN_COM_PASSWD

  Notification Options:
    Specify at least smtpTo if you want to get notification emails.

    --smtpTo=SMTPTO     recipient of email messages. If given then success or
                        failure notifications will be sent to this address.
    --smtpFrom=SMTPFROM
                        sender of email messages
    --smtpServer=SMTPSERVER
                        SMTP server. Default: Environment variable SMTP_SERVER
                        or 'localhost'
    --smtpLogin=SMTPLOGIN
                        login for authentification with SMTP server if needed.
                        Default: Environment variable SMTP_LOGIN
    --smtpPasswd=SMTPPASSWD
                        password for authentification with SMTP serverif
                        needed. Default: Environment variable SMTP_PASSWD""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Thomas Schilz',
      author_email='thschilz @at@ web .dot. de',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "zope.testbrowser",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
