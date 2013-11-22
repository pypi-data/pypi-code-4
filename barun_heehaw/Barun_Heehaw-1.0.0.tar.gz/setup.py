from setuptools import setup

# allow setup.py to be run from any path
#os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

pkgs = ['barun_heehaw']

setup_args = dict(
    name='Barun_Heehaw',
    version='1.0.0',
    description='A sample junk project',
    author='Barun',
    author_email='barunsthakur@gmail.com',
    license='MIT',
    packages=pkgs,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
    ]
)

setup(**setup_args)
