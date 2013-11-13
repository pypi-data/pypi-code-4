#-*- coding: utf-8 -*-
from deploy_class.executors import SSHInterface, ConsoleInterface
from deploy_class.db import MySQLSSHInterface
from deploy_class.cvsystems import MercurialDeployer, SimpleSshDeployer
from deploy_class.globals import bcolors
from deploy_class.hook import Hook
import datetime
import re
from deploy_class.projects import getByDescr
import os


class Deployer:
    """Основной класс, осуществляющий деплой"""
    def __init__(self, 
                     project_path,
                     ssh_user,
                     ssh_host,
                     runapp_prefix = "%s",
                     ssh_password = None,
                     repo_path = None,
                     repo_user = None,
                     repo_password = None,
                     branch = None,
                     log_file = None,
                     pre_commit_hook = None,
                     post_commit_hook = None,
                     docs = None,
                     db = None,
                     deployer="hg",
                     project_type = "py",
                     hooks = {},
                     pull_flags = [],
                     push_flags = [],
                 ):
        """
            :param project_path: - корень проекта на удаленном сервере.(в этой папке должен находиться корень репозитория, .hg или .git)
            :param ssh_user: - ssh-login
            :param ssh_host:
            :param runapp_prefix: - команда для запуска/остановки/перезапуска проекта. Пример: "sv %s circus", где %s может принимать значения start|stop|restart
            :param ssh_password: - пароль ssh. Необязательный (если настроен доступ по RSA ключу)
            :param repo_path: - путь к репу. Параметры репозитория необязательны, если репозиторий настроен (выполняет push, pull без запроса пароля)
            :param repo_user: - логин для репа
            :param repo_password: - пароль для репа
            :param branch: - имя ветки
            :param deployer: - тип деплоера, hg - Mercurial, git - GIT(пока поддерживается только Mercurial)
            :param docs: - bash - интерпретируемая строка для установки документации. Пример::
            
                cd ../docs; make html; cd build/html/deployer; ./deploy.sh install;
            
            :param log_file: - путь к файлу лога на удаленном сервере.
            :param db: - строка подключения к БД на сервере в формате::
            
                (database_type)://(user):(password)@localhost/(database_name)
            :param project_type: - тип проекта, пока поддерживается лишь py (PIP Python project)
        """
        self.hooks = hooks
        self.path = project_path
        self.ssh = SSHInterface(ssh_user, ssh_password, ssh_host, project_path)
        self.console = ConsoleInterface(os.path.abspath(os.path.join(os.getcwd(), "./")))

        self.projectMaker = getByDescr(project_type)(self)
        self.run_prefix = runapp_prefix
        self.branch = branch
        self.docs = docs
        self.log_file = log_file
        self.db = db
        self.push_flags = push_flags
        self.pull_flags = pull_flags

        if self.db:
            self.db_type, self.db_user, self.db_password, self.db_name = re\
                .compile(r"(.*?)://(.*?):(.*?)@localhost/(.*)").findall(db)[0]
                
            if self.db_type == "mysql":
                self.db = MySQLSSHInterface(self.db_user, self.db_password, self.db_name, self.ssh)
            else:
                raise ValueError("Error in branch %s: Unknown db_type: %s"%(self.branch, self.db_type))
        
        if deployer == "hg":
            self.console_deployer = MercurialDeployer(self.console)
            self.remote_deployer = MercurialDeployer(self.ssh, repo_user, repo_password, repo_path)
        elif deployer == "ssh":
            self.console_deployer = self.remote_deployer = SimpleSshDeployer(self)
        else:
            raise ValueError("Incorrect deployer type")

        self.prepareHooks()
    
    def prepareHooks(self):
        for key, value in self.hooks.iteritems():
            self.hooks[key] = Hook(key, value, self)
    
    def has_docs(self):
        return not self.docs is None
    
    def install_docs(self):
        if self.docs is None:
            raise ValueError("Can't install docs. There are no docs in config for branch %s"%self.branch)
        print bcolors.OKGREEN + "Start to install docs" + bcolors.ENDC
        ConsoleInterface().execute(self.docs)
        print bcolors.OKGREEN + "Docs were installed" + bcolors.ENDC
    
    def restart(self, type):
        """Выполняет запуск, остановку или перезапуск проекта на сервере, в зависимости от type
        
            :param type: start|stop|restart
            """
        if not type in ("start", "stop", "restart"):
            raise ValueError("Incorrect type")
        try:
            exs = self.run_prefix%(type)
            print  self.ssh.execute(exs)
        except TypeError:
            pass
    
    def commit(self, message, clean):
        if self.branch:
            print bcolors.OKGREEN+"Updating to branch %s"%self.branch+bcolors.ENDC
            try:
                self.console_deployer.update(branch=self.branch, clean = clean)
            except:
                pass
        self.console_deployer.commit(message)
    
    def install(self):
        """Выполняет следующие действия:
            
            * Коммит текущих изменений
            * Заливка на сервер с сообщением commit_message
            * Подтягивание изменений на удаленном репе
            * Update до последней ревизии
        """
        self.console_deployer.push(self.push_flags)
        self.remote_deployer.pull(self.pull_flags)
        self.remote_deployer.update(branch = self.branch, clean = True)
        self.restart("restart")
        
    
    def show(self, n):
        """Показывает n последних ревизий"""
        self.remote_deployer.show(n)
    
    def update(self, revision, branch, clean):
        """Выполняет update"""
        self.remote_deployer.update(revision, branch, clean)
        
    def setup(self, project = True, clone = True):
        """Выполняет настройку репозитория:
            
            * Клонирует репозиторий
            * Устанавливает зависимости
            * Настраивает параметры репозитория
        """
        self.ssh.execute("mkdir -p %s"%self.path)
        if clone:
            self.remote_deployer.clone(self.path)
        self.remote_deployer.setup()
        if project and self.projectMaker:
            self.projectMaker.install()

        self.remote_deployer.update(branch = self.branch)
        
    def current(self):
        self.remote_deployer.current()
        
    def run_console(self):
        print bcolors.OKGREEN, "Executing console. You now at %s at remote server"%self.path, bcolors.ENDC
        while 1:
            command = raw_input(">>> ")
            if command == "exit":
                break
            print bcolors.WARNING, "<<<OUTPUT:\n", bcolors.ENDC, self.ssh.execute(command)
        
        
    def get_log(self, n=None):
        if self.log_file is None:
            raise ValueError("In branch %s: You try to get log, but there are no log-file in deploy.config"%self.branch)
        print bcolors.OKGREEN+"Start to get log from branch %s"%self.branch+bcolors.ENDC
        if n is None:
            self.ssh.get_file(self.log_file, "%s-log(%s).log"%(self.branch, datetime.datetime.now()))
        else:
            print self.ssh.execute("tail -n %s %s"%(n, self.log_file))
        print bcolors.OKGREEN+"Log was getted."+bcolors.ENDC
    
    def clear_logs(self):
        if self.log_file is None:
            raise ValueError("In branch %s: You try to remove log, but there are no log-file in deploy.config"%self.branch)
        print bcolors.OKGREEN+"Start to rm log from branch %s"%self.branch+bcolors.ENDC
        print "rm %s;"%self.log_file
        self.ssh.sftp.remove(self.log_file)
        print bcolors.OKGREEN+"Log was deleted."+bcolors.ENDC
        
    def get_dump(self):
        if self.db is None:
            raise ValueError("In branch %s: You can't get dump, because no database connect string were detected")
        with open("%s-dump(%s).sql"%(self.branch,datetime.datetime.now()), "w") as fd:
            print >>fd, self.db.get_dump()
        