from setuptools import setup

setup(
    name="crszu",
    packages=["crszu"],
    version="0.0.1",
    license="MIT License",
    install_requires=["pillow"],
    description="captcha regonization for SZU authentication.",
    author="MarkNV",
    author_email="marknv1991@gmail.com",
    url="https://github.com/marknv/crszu",
    test_suite="nose.collector",
    tests_require=["nose"],
    include_package_data=True
)
