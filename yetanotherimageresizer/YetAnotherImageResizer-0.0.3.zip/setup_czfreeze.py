from cx_Freeze import setup, Executable

include_files = [ ('imageresizer/logger.ini', 'logger.ini') ]
setup(
    name='YetAnotherImageResizer',
    version='0.0.3',
    author='Mathieu Roche',
    author_email='mathieu.roche-site@laposte.net',
    packages=['imageresizer', 'imageresizer.test'],
    package_data = {'imageresizer':['logger.ini']},
    scripts = [ "bin/imageresizer" ],
    url='http://pypi.python.org/pypi/YetAnotherImageResizer/',
    license='LICENSE.txt',
    description='Image resizer for Piwigo with Tk UI.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PIL >= 1.1.6",
    ],
	options = {'build_exe': {'include_files':include_files}},
	executables = [Executable( script = "bin\\imageresizer"
	#, base="Win32Gui"
	)],	
)
 
