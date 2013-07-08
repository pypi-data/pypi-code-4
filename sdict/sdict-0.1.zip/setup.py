from distutils.core import setup,Extension
tst_module = Extension('_tst',sources=['sdict/tst_wrap.cpp','sdict/tst.cpp'])

setup(name='sdict',
	version='0.1',
	author='Sun, Junyi',
	description='Sorted Dictionary Implementation',
	ext_modules=[tst_module],
	packages=['sdict'],
	package_dir={'sdict':'sdict'}	
)

