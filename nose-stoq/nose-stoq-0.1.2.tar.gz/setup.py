from setuptools import setup

setup(name='nose-stoq',
      version='0.1.2',
      zip_safe=True,
      author="Johan Dahlin",
      author_email="stoq-devel@async.com.br",
      url="http://www.stoq.com.br/",
      description="A nose plugin for Stoq",
      license="MIT",
      py_modules=['stoqplugin'],
      entry_points = {
        'nose.plugins': ['stoq = stoqplugin:StoqPlugin']
        },)
