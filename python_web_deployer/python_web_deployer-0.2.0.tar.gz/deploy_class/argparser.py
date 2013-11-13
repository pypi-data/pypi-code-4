#-*- coding: utf-8 -*-
from deploy_class.globals import bcolors
import argparse
import logging

DESCRIPTION = u"""Python WEB deployer, v0.0.1
----------------------------------------------------
Usage:

./deploy.py {branch}|console 
    [install     #устанавливает на сервер
        [--commit {message}]    #сделать коммит перед установкой
        [--docs]                #установить документацию после установки
    ] |
    [show         #показывает дерево установленных на сервере ревизий
        [-n {count}]    #число ревизий
    ] |
    [update         #выполняет update до ревизии или ветки на сервере
        [-r {revision} |     #ревизия
        -b {branch}]] |      #ветка
    [setup                 #выполняет удаленную настройку репозитория
        [--no-project]    # не устанавливать virtualenv, dependencies etc.
        [--no-clone]      # не клонировать реп
    ] |
    [current] |            #текущая версия на сервере
    [docs install] |        #установить документацию
    [log 
        [get             #получение лога
            [-n {count rows}]    
        [clear]] |        #удаление лога
    [db getdump] |        #получение дампа БД
    [start|stop|restart]    #запуск/остановка сервера
        
* ./deploy.py console запускает real-time выполнение комманд деплоера.                  

* branch - ветка для разработки. Доступные ветки указываются в файле deploy.config

* action - Действие. Доступные действия:
    - install - установка текущей ветки на удаленный сервер. Дополнительные опции --commit <message>, --docs
    - show -n <n> - показать n последних ревизий на сервере.
    - update -r <revision> | -b <branch> - откат к ревизии или бранчу на сервере
    - setup - выполняет настройку репозиториев на удаленном сервере. 
        --no-project - не выполнять настройку проекта (установка зависимостей, создание virtualenv)
        --no-clone - не клонировать репозиторий
    - current - показывает текущую версию удаленнго репозитория
    - docs:
        - docs install - выполняет установку документации.
    - log:
        - log get - получение файла лога с удаленного сервера. Дополнительная опция -n <count rows>
        - log clear - очистка(удаление) лога на сервере
    - db:
        - db getdump - получение дампа базы данных (должна быть настроена директива db)
    - start|stop|restart - перезапуск сервера.

"""

class ArgParser:
    def __init__(self, DEPLOYERS):
        self.DEPLOYERS = DEPLOYERS
        self._initializeParser()
    
    def console(self):
        input = ""
        print bcolors.OKGREEN, "Welcome to realtime deployer interface. For help use -h or --help", bcolors.ENDC
        while 1:
            input = raw_input("Please input command\n")
            if input == "exit":
                break
            input = input.split(" ")
            try:
                self._parse(input)
            except Exception as x:
                logging.exception(x)
    
    def parse(self, data):
        self._parse(data)
    
    def _initializeParser(self):
        arg_parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
        
        arg_parser.add_argument("branch", action="store", nargs = "?")
        arg_parser.add_argument("action", action="store", nargs = "?")
        arg_parser.add_argument("action2", action="store", nargs = "?")
        
        arg_parser.add_argument("--commit", action="store", help=u"Делать ли коммит при установке или нет.", default = False)
        
        arg_parser.add_argument("-r", "--revision", action="store", 
                                help=u"Ревизия для отката", default=None, type=int)
        arg_parser.add_argument("-b", "--update-branch", action="store", 
                                help=u"Ветка для отката", default=None)
        arg_parser.add_argument("-n", action="store", nargs="?", 
                                default = None, help=u"Количество ревизий. Используется для show и log get", type=int)
        
        
        arg_parser.add_argument("--setup", action="store_true", help = u"Установка деплоера.")
        arg_parser.add_argument("--docs", action="store_true", help=u"Установить документацию")
        arg_parser.add_argument("--no-project", action = "store_true", 
                                help=u"Не выполнять установку проекта при setup")
        arg_parser.add_argument("--no-clone", action = "store_true", 
                                help=u"Не клонировать репозиторий при установке проекта")
        
        
        arg_parser.add_argument("--clean", action = "store_true",
                                help=u'Отбрасывать удаленные изменения при update',
                                default = False)
    
        self.arg_parser = arg_parser
    
    def _parse(self, data):
        self.args = self.arg_parser.parse_args(data)
        self.parseInit()
    
    def parseInit(self):
        self.parseBranch()
        self.parseAction()
            
    def parseBranch(self):
        if self.args.branch == "console":
            self.console()
        
        if not self.args.branch or self.args.branch not in self.DEPLOYERS:
            raise ValueError("Incorrect argument branch")
        
        self.deployer = self.DEPLOYERS[self.args.branch]

        self.deployer.ssh.connect()
    
    def parseAction(self):
        action = self.args.action
        if action == "install":
            self.parseInstallAction()
        elif action == "show":
            self.parseShowAction()
        elif action == "update":
            self.parseUpdateAction()
        elif action == "setup":
            self.parseSetupAction()
        elif action == "current":
            self.deployer.current()
        elif action == "docs":
            self.parseDocsAction()
        elif action == "log":
            self.parseLogAction()
        elif action == "db":
            self.parseDbMethods()
        elif action == "console":
            self.deployer.run_console()
        elif action in ("start", "stop", "restart"):
            self.deployer.restart(self.args.action)  
        elif action == "hooks":
            self.parseHookMethods()
        else:
            raise ValueError("Incorrect action")    
              
    def parseDocsAction(self):
        if self.args.action2 == "install":
                self.deployer.install_docs()
        else:
            raise ValueError("Incorrect action2")
    
    def parseInstallAction(self):
        if self.args.commit:
            self.deployer.commit(self.args.commit, clean = False)
        self.deployer.install()
        if self.args.docs:
            if not self.deployer.has_docs():
                raise ValueError("You try to set docs, but no docs founded in branch %s. Please, check your deploy.config"%(deployer.branch))
            self.deployer.install_docs()
            
    def parseShowAction(self):
        self.deployer.show(self.args.n)
        
    def parseUpdateAction(self):
        self.deployer.update(revision = self.args.revision, branch = self.args.update_branch, clean = self.args.clean)
        
    def parseSetupAction(self):
        self.deployer.setup(project = (not self.args.no_project), clone = (not self.args.no_clone))
        
    def parseLogAction(self):
        if self.args.action2 == "get":
            self.deployer.get_log(self.args.n)
        elif self.args.action2 == "clear":
            self.deployer.clear_logs()
        else:
            raise ValueError("Incorrect action2")
    
    def parseDbMethods(self):
        if self.args.action2 == "getdump":
            self.deployer.get_dump()
        else:
            raise ValueError("Unknown action2: %s"%self.args.action2)
        
    def parseHookMethods(self):
        self.deployer.hooks[self.args.action2].execute()
        
    