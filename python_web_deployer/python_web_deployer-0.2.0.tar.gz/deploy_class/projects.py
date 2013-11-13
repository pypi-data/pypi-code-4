#-*- coding: utf-8 -*-
from deploy_class.globals import NotOveroadedError, bcolors

class AbstractProject:
    def install(self):
        raise NotOveroadedError()
    
class PythonProject:
    def __init__(self, deployer):
        self.path = deployer.path
        self.deployer = deployer
        if not self.path: raise ValueError("Argument `path` of PythonProject is required")


    def make_env(self):
        """
        Makes virtualenv for project.
        
        .. note::
        
            It creates folder **env** in root of your folder, so, env/* must be in your ignore file.
            
        """
        print bcolors.OKGREEN, "Making virtualenv"
        self.deployer.ssh.execute("""
virtualenv env;
        """)
        print bcolors.ENDC
    
    
    def install_req(self):
        """
            Installs requirements. In python projects it runs python setup.py develop from project env
        """
        self.deployer.ssh.execute("""
. env/bin/activate;
python setup.py develop;
        """)
    
    def install(self):
        self.make_env()
        self.install_req()

def getByDescr(desc):
    try:
        return {
            "py": PythonProject
                }.get(desc)
    except KeyError:
        raise ValueError("Incorrect project tag")