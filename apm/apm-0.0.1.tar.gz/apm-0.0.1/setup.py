from setuptools import setup

setup(
  name='apm',
  version='0.0.1',
  author='Yamil Asusta (elbuo8)',
  author_email='yamil.asusta@upr.edu',
  scripts=['apm'],
  url='https://github.com/elbuo8/apm',
  download_url='https://github.com/elbuo8/apm/tarball/master',
  license='MIT',
  description='Ansible Playbook Manager CLI tool',
  long_description='Publish and download playbooks/roles from APM',
  install_requires=[
    'requests',
    'pyyaml'
  ],
)
