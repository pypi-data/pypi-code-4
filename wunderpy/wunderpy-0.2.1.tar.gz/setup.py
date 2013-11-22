from setuptools import setup, find_packages

try:
    desc_file = open("README.rst")
    description = desc_file.read()
    desc_file.close()
except:
    description = ""


setup(
    name="wunderpy",
    version="0.2.1",
    author="bsmt",
    author_email="bsmt@bsmt.me",
    url="https://github.com/bsmt/wunderpy",
    license="MIT",
    description="An experimental wrapper for the Wunderlist 2 API",
    long_description=description,
    classifiers=['Development Status :: 4 - Beta',
                'License :: OSI Approved :: MIT License',
                'Intended Audience :: Developers',
                'Natural Language :: English',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
                'Topic :: Utilities',
                'Topic :: Documentation',
                'Environment :: Console'
                 ],
    packages=find_packages(exclude=("tests",)),
    install_requires=["requests>=1.1.0"],
    entry_points={'console_scripts': ['wunderlist = wunderpy.cli.main:main']}
)
