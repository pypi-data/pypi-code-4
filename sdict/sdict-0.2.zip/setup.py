from distutils.core import setup,Extension
import sys,os

D = os.path.dirname(__file__)

tst_module = Extension('_tst',
    sources=[
        os.path.join(D,'sdict/tst_wrap.cpp'),
        os.path.join(D,'sdict/tst.cpp')
    ]
)

setup(name='sdict',
	version='0.2',
	author='Sun, Junyi',
	description='Sorted Dictionary Implementation',
	ext_modules=[tst_module],
	packages=['sdict'],
	package_dir={'sdict':'sdict'}	
)

