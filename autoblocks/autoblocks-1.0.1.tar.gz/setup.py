from setuptools import setup, find_packages
import os

setup(
    name='autoblocks',
    author='Luke Hutscal',
    author_email='support@strathcom.com',
    platforms=['OS Independent'],
    license='BSD License',
    version='1.0.1',
    description="Place arbitrary django-cms placeholders into templates",
    long_description=open(
        os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/Strathcom/django-cms-autoblocks',
    install_requires=[
        'django-cms>=2.4.1',
    ],
    packages=find_packages(),
)
