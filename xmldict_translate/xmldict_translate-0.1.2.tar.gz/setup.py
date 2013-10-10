from setuptools import setup, find_packages
from os.path import join, dirname
import xmldict_translate

setup(
    name='xmldict_translate',
    version=xmldict_translate.__version__,
    author=xmldict_translate.__author__,
    author_email=xmldict_translate.__author_email__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
)
