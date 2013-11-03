from distutils.core import setup

setup(
    name='constractor',
    version='0.1.0',
    author='David Kuryakin',
    author_email='dkuryakin@gmail.com',
    packages=['constractor', 'constractor.test'],
    scripts=['bin/constractor_train.py','bin/constractor_predict.py'],
    url='http://pypi.python.org/pypi/constractor/',
    license='LICENSE.txt',
    description='Smart web page content extractor.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.8.0",
        "scikit-learn >= 0.14.1",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ]
)