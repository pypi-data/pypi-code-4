from setuptools import setup, find_packages
import os


setup(name="nose-colorxunit",
        version = "0.1.4",
        author = "Lesus",
        author_email = "walkingnine@gmail.com",
        license = "Apache License, Version 2.0",
        url="https://github.com/walkingnine/colorunit",
        description = "make unittest formatted and colorful output",
        long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
        zip_safe = False,
        keywords = "nose nosetest xunit",
        py_modules = ["colorunit"],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent", 
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Software Development :: Testing",
            ],
        install_requires = [
            "nose>=0.10",
            "colorama>=0.2.5",
            ],
        entry_points = {
            'nose.plugins.0.10':[
                "colorunit = colorunit:ColorUnit"
                ]
            }
        
        )
