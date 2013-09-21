from setuptools import setup

setup(name='dnsq',
      description='DNS Query Tool',
      author='Mailgun (Rackspace)',
      author_email='admin@mailgunhq.com',
      version='1.0',
      py_modules=['dnsq'],
      zip_safe=True,
      install_requires=[
        'dnspython==1.11.1',
      ],
      )
