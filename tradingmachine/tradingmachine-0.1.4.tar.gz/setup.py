from setuptools import setup, find_packages

LONG_DESCRIPTION = None
README_MARKDOWN = None

with open('ReadMe.md') as markdown_source:
    README_MARKDOWN = markdown_source.read()

LONG_DESCRIPTION = README_MARKDOWN

setup(
    name='tradingmachine',
    version='0.1.4',
    description='A backtester for financial algorithms.',
    author='Chen Huang',
    author_email='chinux@gmail.com',
    packages=find_packages(),
    long_description=LONG_DESCRIPTION,
    license='BSD',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing',
    ],
    install_requires=[
        'pytz',
        'numpy',
        'matplotlib',
        'pandas',
        'ta-lib'
    ],
    url="https://gitlab.com/chinux23/tradingmachine"
)
