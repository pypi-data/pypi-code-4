from setuptools import setup, find_packages

setup(
        author='Ana Nelson',
        author_email='ana@ananelson.com',
        classifiers=[
            "License :: OSI Approved :: MIT License"
            ],
        description='Plugin System',
        entry_points = {
            },
        include_package_data = True,
        install_requires = [
            ],
        name='cashew',
        packages=find_packages(),
        url='http://dexy.github.io/cashew/',
        version="0.2.3"
        )
