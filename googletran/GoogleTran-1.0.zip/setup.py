# encoding: utf-8

import GoogleTran
from distutils.core import setup
def install():
    setup(
          name = 'GoogleTran',
          version = "1.0",
          description='Google Translate (Web) API for Python',
          author = 'bebound',
          url = 'https://github.com/bebound/GoogleTran',
          author_email = 'bebound@gmail.com',
          packages=['GoogleTran'],
          )

if __name__ == "__main__":
    install()