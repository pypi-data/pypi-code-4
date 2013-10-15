
from setuptools import setup

setup(
    name='etiquetando',
    description='Term extractor (tags) for Brazilian Portuguese (pt-br)',
    version=0.1,
    packages=['etiquetando'],
    author='Sergio Oliveira',
    author_email='sergio@tracy.com.br',
    url='http://github.com/TracyWebTech/etiquetando',
    license='BSD',
    install_requires=['stemming>=1.0', 'repoze.lru>=0.6'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: Portuguese (Brazilian)',
        ],
)
