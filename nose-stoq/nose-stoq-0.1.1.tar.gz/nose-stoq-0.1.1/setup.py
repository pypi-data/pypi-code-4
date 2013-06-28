from setuptools import setup, find_packages

setup(name='nose-stoq',
      version='0.1.1',
      packages=find_packages(),
      package_data={'': ['LICENSE']},
      zip_safe=True,
      author="Johan Dahlin",
      author_email="stoq-devel@async.com.br",
      url="http://www.stoq.com.br/",
      description="A nose plugin for Stoq",
      license="MIT",
      entry_points = {
        'nose.plugins': ['stoq = stoqplugin:StoqPlugin']
        },)
