from setuptools import setup, find_packages

setup(name="csp-validator",
      version="0.1",
      description="Content-Security-Policy validator",
      author="Yeuk Hon Wong",
      classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Security',
      ],
      author_email="yeukhon@mozilla.com",
      install_requires=['parsimonious==0.5',],
      packages=find_packages(),
      include_package_data=True,
)
