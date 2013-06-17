from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='vmessage',
      version='0.1.0',
      author='Keisuke Minami',
      description='Read only support for a vMessage mailbox.',
      long_description=long_description,
      url='https://github.com/kminami/python-vmessage',
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python',
                   'Topic :: Communications :: Email',
                  ],
      packages=['vmessage'],
     )
