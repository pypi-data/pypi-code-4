from distutils.core import setup, Extension

module1 = Extension('fmetrics',
                    extra_compile_args = ['-std=c99', '-O3'],
                    extra_link_args = ['-lm', '-lpng'],
                    include_dirs = ['/usr/include/', '/opt/local/include'],
                    library_dirs= ['/usr/lib/', '/opt/local/lib'],
                    sources = ['fmetric.c'],
                    depends = ['fmetric_py.h'])

setup (name = 'fmetrics',
       version = '1.0',
       description = 'Contains routines to calculate precision, recall and f-measure',
       ext_modules = [module1])
