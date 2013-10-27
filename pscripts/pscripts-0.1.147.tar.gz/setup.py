from setuptools import setup
from setuptools.command.install  import  install  as  _install
from setuptools import setup
import os
version='0.1.147'
name='pscripts'
scripts = [
    'scripts/python-deployment',
    'scripts/hdmi_brightness',
    'scripts/update_external_ip',
    'scripts/cp_exe_2_chroot_jail',
    'scripts/process_attach',
]
classifiers = [ 'Programming Language :: Python :: 3.3',
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Natural Language :: English',
                'Operating System :: POSIX :: Linux',
                'Topic :: System :: Systems Administration',
                'Topic :: Utilities',
            ]
install_requires=[
    'setuptools',
    'SimpleDaemon >= 1.3.0',
    'PyYAML >= 3.10',
    'pidfile >= 0.1.0',
    ]
data_files=[('/etc/external_ip_updater/', 
             ['config/urls.yaml.generic','config/config.conf.generic']),
            ('/etc/systemd/system/',
             ['config/update_external_ip.service']),]

conf_dir="/etc/external_ip_updater/"

# this nonesense is so that we have a way to not over-write the 
# config files of previous installs.  If they are present it
# just adds them to that directory with a *.generic suffix.
class install(_install):
    def run(self):
        _install.run(self)
        self.mv_file_if_not_present("urls.yaml")
        self.mv_file_if_not_present("config.conf")

    def mv_file_if_not_present(self, conf_file):
        if not os.path.isfile( conf_dir + conf_file ): 
            os.rename(conf_dir + conf_file + ".generic", conf_dir + conf_file)
            
setup(
    name = name,
    version = version,
    packages = [name],
    description = 'Automation Scripts for Linux',
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='www.google.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='Automates some python deployment steps',
    classifiers=classifiers,
    scripts = scripts,
    data_files=data_files,
    install_requires=install_requires,
    cmdclass={'install': install},
)
