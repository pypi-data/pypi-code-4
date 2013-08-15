from setuptools import setup

setup(
    name="imaper",
    version="1.0.0",
    author="Dan Horrigan",
    author_email="dan@dhorrigan.com",
    url="https://bitbucket.org/dhrrgn/imaper",
    description="IMAP made easy.",
    long_description="See documentation at http://pythonhosted.org/imaper/",
    license='MIT',
    packages=["imaper"],
    install_requires=[
        "IMAPClient==0.10.2",
    ],
    classifiers=[
        "Topic :: Utilities",
    ],
)
