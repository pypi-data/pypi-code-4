#-*- coding: utf-8 -*-
import re
class Hook:
    """Основной класс для хука.
    
        :param name: - ключ, по которому будет вызываться hook
        :param 
    
            {pre|post}.{local|remote}.{file|string}::<string|file_path>
        
        Пример::
        
            pre.local.file::/home/stas/project/hook.sh
            post.local.string::cd ../; ./docs_install.sh
    """
    PATT = re.compile(r"(local|remote)\.(file|string)\:\:(.*)")
    def __init__(self, name, string, deployer, description = None):
        self.name = name
        self.deployer = deployer
        self.where, self.what, self.data = self.PATT.findall(string)[0]
    
    def getExecutor(self):
        return {
                    "local": self.deployer.console,
                    "remote": self.deployer.ssh
                }[self.where]
    
    def execute(self):
        print "Executing hook..."
        if self.what == "file":
            print self.getExecutor().execute("./"+self.data)
        else:
            print self.getExecutor().execute(self.data)