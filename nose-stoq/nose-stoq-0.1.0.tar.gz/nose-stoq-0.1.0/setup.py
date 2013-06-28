from setuptools import setup

setup(name='nose-stoq',
      version='0.1.0',
      author="Johan Dahlin",
      author_email="stoq-devel@async.com.br",
      url="http://www.stoq.com.br/",
      description="A nose plugin for Stoq",
      license="MIT",
      entry_points = {
        'nose.plugins': ['stoq = stoqplugin:StoqPlugin']
        },)
