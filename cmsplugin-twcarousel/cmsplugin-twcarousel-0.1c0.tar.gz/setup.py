from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_desc = file.read()

version = __import__('twcarousel').get_version()

setup(
    name='cmsplugin-twcarousel',
    version=version,
    author='Kevin Van Wilder',
    author_email='kevin@van-wilder.be',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/kevwilde/cmsplugin-twcarousel',
    license='BSD',
    description='A Twitter Bootstrap Carousel plugin for Django CMS.',
    long_description=long_desc,
    include_package_data=True,
    zip_safe=False,
    install_requires=(
    ),
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries',
    ],
)