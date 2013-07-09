from setuptools import setup, find_packages

dependencies = []

setup(
    name="cheap",
    version="0.1",
    packages=find_packages(),
    install_requires=dependencies,
    author="Cheaper Machine Locator.",
    author_email="team@cheaper.io",
    description="A service for locate and get the cheaper available VM",
    keywords="cloud cloud-computing cheap cheap vms hypervisor amazon",
    license="BSD",

    classifiers=['Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'Operating System :: Unix ']
)
