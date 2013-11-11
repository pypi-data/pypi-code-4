#! /usr/bin/env python
# coding: utf-8

import sys
import os
from setuptools import setup, find_packages
from setuptools.command import install_lib

name_space = 'ruamel'
full_package_name = name_space + '.rmoldkernels'

exclude_files = [
    'setup.py'
]

class MyInstallLib(install_lib.install_lib):
    "create __init__.py on the fly"
    def run(self):
        from textwrap import dedent
        install_lib.install_lib.run(self)
        init_txt = dedent('''\
            # coding: utf-8
            # Copyright © 2013 Anthon van der Neut, RUAMEL bvba
            "generated __init__.py "
            try:
                __import__('pkg_resources').declare_namespace(__name__)
            except ImportError:
                pass
        ''')
        init_path = full_package_name.split('.')[:-1]
        for product_init in [
            os.path.join(
                *([self.install_dir] + init_path[:p+1] + ['__init__.py']))
                for p in range(len(init_path))
        ]:
            if not os.path.exists(product_init):
                print('creating %s' % product_init)
                with open(product_init, "w") as fp:
                    fp.write(init_txt)
        setup = os.path.join(self.install_dir, 'setup.py')
        print '>' * 72
        print 'setup', os.path.exists(setup), setup

    def install(self):
        fpp = full_package_name.split('.')  # full package path
        full_exclude_files = [os.path.join(*(fpp + [x])) for x in exclude_files]
        alt_files = []
        outfiles = install_lib.install_lib.install(self)
        #print '<' * 60, '\n', outfiles
        for x in outfiles:
            for full_exclude_file in full_exclude_files:
                if full_exclude_file in x:
                    os.remove(x)
                    break
            else:
                alt_files.append(x)
        print '<' * 60
        for x in alt_files:
            print '   ', x.split('site-packages/')[-1]

        return alt_files


def main():
    install_requires = [
        ]
    packages = [full_package_name] + [(full_package_name + '.' + x) for x \
                                        in find_packages(exclude=['tests'])]
    print 'packages', packages
    setup(
        name=full_package_name,
        version="0.1.0",
        description="remove no longer needed Ubuntu kernels",
        install_requires=[
        ],
        #install_requires=install_requires,
        long_description="Long Description",
        url='https://bitbucket.org/anthon_van_der_neut/' + full_package_name,
        author='Anthon van der Neut',
        author_email='a.van.der.neut@ruamel.eu',
        license='Copyright Ruamel bvba 2007-2013',
        package_dir={full_package_name: '.'},
        namespace_packages = [name_space],
        packages=packages,
        scripts=['rmoldkernels'],
        #entry_points=mk_entry_points(full_package_name),
        cmdclass={'install_lib': MyInstallLib},
        classifiers=['Development Status :: 4 - Beta',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
        ]
    )

def mk_entry_points(package_name):
    script_name = package_name.replace('.', '_')
    return {'console_scripts': [
        '{} = {}:main'.format(script_name, package_name),
    ]}

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sdist':
        assert  full_package_name == os.path.abspath(os.path.dirname(
            __file__)).split('site-packages' + os.path.sep)[1].replace(
                os.path.sep, '.')
    main()
