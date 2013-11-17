"""
Flask SocialShare
-----------------

"""
from setuptools import setup

setup(
    name="Flask-SocialShare",
    version="0.0.1",
    url="",
    license="BSD",
    author="Paul d'Hubert",
    author_email="contact@pauldhubert.com",
    description="Flask social sharing helpers",
    long_description=__doc__,
    py_modules=["flask_socialshare"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "flask"
        ],
    classifiers=[]
    )
