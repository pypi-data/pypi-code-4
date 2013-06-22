import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-makemessages-plus',
    version='0.1',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=False,
    license='BSD License',  # example license
    description='An django extension to support making messages from coffeescript files',
    long_description=README,
    url='http://github.com/hoozecn/django-makemessages-plus',
    author='Zhimin Wu',
    author_email='hoozecn+dcmm@gmail.com',
    classifiers=[
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License', # example license
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.7',
      'Topic :: Internet :: WWW/HTTP',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
    install_requires = [
      'django>=1.2'
      ]
)
