from setuptools import setup

setup(name='persona-test-user',
      version='0.1',
      description='Generate Persona Test Accounts',
      author='Florin Strugariu, Zac Campbell',
      author_email='bebe@mozilla.ro',
      url='https://github.com/bebef1987/persona-test-user',
      packages=['persona_test_user'],
      install_requires=[],
      license='Mozilla Public License 2.0 (MPL 2.0)',
      long_description="""
A base test class that can be extended by other tests to include utility methods.
API docs: https://github.com/mozilla/personatestuser.org#api

Usage:
verified = bool:
Verified refers to the user's account and password already approved and set up

env = str:
Strings "dev", "stage" or "prod" will return users for the respective environments
If "None" a production Persona user will be returned.

env = dict:
For custom browserid databases and verifiers
self.user = PersonaTestUser().create_user(verified=True,
env={"browserid":"firefoxos.persona.org", "verifier":"firefoxos.123done.org"})

      """,
      keywords='',
      classifiers=[])
