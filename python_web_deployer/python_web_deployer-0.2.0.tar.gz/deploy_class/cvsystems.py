#-*- coding: utf-8 -*-
from deploy_class.globals import NotOveroadedError, bcolors
from deploy_class.executors import ConsoleInterface
import uuid

class _DeployStrategyAbstractInterface:
    """Абстрактный интерфейс для управления системами контроля версий.(GIT, Mercurial)"""
    def __init__(self, user, password, repo, branch, execute_interface):
        """
            :param user: Логин
            :param password: пароль
            :param repo: репозиторий
            :param branch: ветка разработки
            :param execute_interface: Интерфейс для выполнения консольных комманд.
        """
        raise NotOveroadedError
    
    def commit(self, commit_message):
        """Выполняет коммит"""
        raise NotOveroadedError
    
    def push(self):
        """Выполняет push на сервер. Репозиторий должен быть правильно сконфигурирован."""
        raise NotOveroadedError
        
    def show(self, n=None):
        """Просмотр n последних ревизий"""
        raise NotOveroadedError
    
    def pull(self):
        """Выполняет pull"""
        raise NotOveroadedError
        
    def update(self, revision=None, branch=None):
        """Выполняет update на ревизию или на ветку. Ревизия имеет больший приоритет"""
        print "\n\n\n", "Some bad happens", "\n\n\n"
        raise NotOveroadedError
    
    def setup(self):
        """Выполняет конфигурирование репозитория"""
        raise NotOveroadedError

class SimpleSshDeployer(_DeployStrategyAbstractInterface):
    """
        Деплоер, который использует передачу файлов через ssh напрямую для деплоинга.
        
        .. warning::
        
            Поддерживается только в Linux либо в Windows cygwin.

    """
    def __init__(self, app):
        self.app = app
    
    def push(self, *a, **k):
        self.archName = "/tmp/%s.zip"%str(uuid.uuid4())
        self.app.console.execute("zip -r -o %s *"%self.archName)
        self.app.ssh.upload_file(self.archName, self.archName)
        self.app.ssh.execute("unzip -o %s -d %s"%(self.archName, self.app.path))
    
    def pull(self, *a, **k):
        pass

    def update(self, *a, **k):
        pass
        

class MercurialDeployer(_DeployStrategyAbstractInterface):
    def __init__(self, execute_interface, user = None, password = None, repo = None):
        self.execute_interface = execute_interface
        self.repostring = None
        if repo:
            if not "@" in repo:
                self.repostring = repo.replace("://", "://"+user+":"+password+"@")
            
    def commit(self, commit_message):
        commit_message = commit_message.replace(" ", "_").replace("\t", "_").replace("\n", "_")
        print bcolors.WARNING + "Check you branch and changes before commit" + bcolors.ENDC
        print self.execute_interface.execute("hg summary")
        print bcolors.WARNING+"Next check status of changes"+bcolors.ENDC
        print self.execute_interface.execute("hg status")
        if True or raw_input("\n"+bcolors.WARNING+ "Are you sure?"+bcolors.ENDC+"\nY/N\n") in ("Y", "y", "yes", "YES", "Yes", "Да", "да"):
            try:
                print self.execute_interface.execute("hg commit -A -m " + commit_message)
            except:
                print bcolors.FAIL + "Cannot commit. Maybe no changes?"+bcolors.ENDC
        else:
            raise ValueError("Commit discarded. Exiting...")
            
    def push(self, push_flags = []):
        print bcolors.OKGREEN + "Start to push"+bcolors.ENDC
        try:
            print self.execute_interface.execute("hg push "+" ".join(push_flags))
        except:
            print bcolors.FAIL + "Cannot push. Maybe no changes?"+bcolors.ENDC
        print bcolors.OKGREEN + "end push"+bcolors.ENDC
        
    def show(self, n=None):
        a = "hg glog "
        if n:
            a += "-l " + str(n)
        print self.execute_interface.execute(a)
    
    def pull(self, pull_flags = []):
        print self.execute_interface.execute("hg pull "+" ".join(pull_flags))
        
    def update(self, revision=None, branch=None, clean = False):
        print bcolors.OKGREEN+"Updating mercurial repo. Params: revision(%s), branch(%s)"%(revision, branch)+bcolors.ENDC
        execute_string = "hg update"
        if clean:
            execute_string += " -C"
        if revision:
            execute_string += " "+str(revision)
        elif branch:
            execute_string += " "+str(branch)
            
        print self.execute_interface.execute(execute_string)
    
    def current(self):
        print bcolors.OKGREEN + "Current repo status:" + bcolors.ENDC
        print self.execute_interface.execute("hg summary")
    
    def clone(self, to):
        if not self.repostring:
            raise ValueError("Try to clone repo, but no info about repository in config")
        print bcolors.OKGREEN, "Cloning repos", bcolors.ENDC
        self.execute_interface.execute("hg clone %s %s"%(self.repostring, to))
    
    def setup(self):
        if self.repostring is None:
            raise ValueError(u"Попытка настроить систему контроля версий, для которой не передан path")
        string = """[ui]
username = Server

[paths]
default = %(path)s

[extensions]
graphlog = """%{"path": self.repostring}
        print self.execute_interface.execute("ls", "echo '%s' > .hg/hgrc"%string)