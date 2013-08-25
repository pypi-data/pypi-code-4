from setuptools import setup, find_packages
import os


setup(name="nose-colorxunit",
        version = "0.1.5",
        description = "make unittest formatted and colorful output(cross platform)",
        long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
        license = "Apache License,Version 2.0",
        author = "Lesus",
        author_email = "walkingnine@gmail.com",
        url="https://github.com/walkingnine/colorunit",
        py_modules = ["colorunit"],
        zip_safe = False,
        keywords = "nose nosetest xunit",
        classifiers = [
            "Development Status :: 3 - Alpha",
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
