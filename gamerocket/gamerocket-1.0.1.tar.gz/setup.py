from setuptools import setup

setup(
    name = "gamerocket",
    version = "1.0.1",
    packages = ["gamerocket", "gamerocket.exceptions", "gamerocket.result", "gamerocket.util", "gamerocket.util.http_strategy", "gamerocket.ssl"],
    package_data={"gamerocket": ["ssl/*"]},

    install_requires=["pycurl>=7.19.0"],
    
    url = "https://www.gamerocket.io/docs/python/sdk",
    description = "Gamerocket Python Client Library",
    author = "Workbandits",
    author_email = "contact@gamerocket.io"
)
