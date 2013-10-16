#-*- coding: utf-8 -*-
import sqlahelper
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Integer, Text, Enum
from sqlalchemy.ext.hybrid import hybrid_property
import hashlib
import random
from sqlalchemy.orm import relationship
from pyramid_rest.models_crud import constructSuperModel, CRUD
import time
from pyramid_rest.config import Config
from pyramid_rest.logger import Logger
from sqlalchemy.dialects.mysql.base import MSText
from pyramid_rest.exceptions import UnknownError
import transaction

Base = sqlahelper.get_base()

USER_GROUPS = ["main",
               "admin",
               "new",
               "banned"]


class Users(Base, CRUD):
    __tablename__ = "_rest_users"
    id = Column(Integer, primary_key = True)
    type = Column(String(200))
    __mapper_args__ = {'polymorphic_identity': '_rest_users',
                       'polymorphic_on': type}
    
    email = Column(String(200), unique = True)
    group = Column(Enum(*USER_GROUPS, name = "user_groups"), default = "new")
    
    _password = Column(String(100))
    
    @classmethod
    def generate_password(cls, value):
        return hashlib.sha256(str(value)).hexdigest()
    
    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def _set_password(self, value):
        self._password = self.generate_password(value)
    
    def check_password(self, value):
        return (self._password == self.generate_password(value))
    
    def add_session(self):
        db_session = Sessions()._add()
        self.sessions += [db_session]
        return db_session
    
    def logout(self):
        self.sessions = []
        
    def __init__(self, *a, **k):
        Base.__init__(self, *a, **k)

 
class Sessions(Base, CRUD):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("_rest_users.id", ondelete = "cascade"))
    sid = Column(String(200), unique = True)
    
    user = relationship(Users, backref = "sessions")
    
    def __init__(self, *a, **k):
        k["sid"] = hashlib.sha256(str(random.randrange(10, 10**100))).hexdigest()
        Base.__init__(self, *a, **k)

class AbstractConfirmateActionHandler:
    """
        Интерфейс для 
    """

class AbstractConfirmateAction(Base, CRUD):
    """
        Класс, для подтверждения некоторых изменений.
        
        * Изменением считается изменение некоторого поля объекта в таблице в БД.
        * На set событие данного поле навешивается событие, которое обрабатывается некоторым handler'ом. При этом в таблицу-наследник AbstractConfirmateAction вносится
        запись об изменении. Запись действительна в течении request.security.confirmation.life_time секунд.
        * Каждая запись имеет статус: init, sended, finished, 
        
    """
    logger = Logger().security.getChild("confirmation")
    
    table = None
    """
        ORM класс таблицы
    """
    field = None
    """
        строка - название поля изменене которого нужно подтверждать
    """
    
    __tablename__ = "_rest_actions_confirmations"
    __table_args__ = (UniqueConstraint("code", "owner_id"),)
    
    id = Column(Integer, primary_key = True)
    
    object_id = None
    """
        id объекта, изменение которого отслеживаем. Колонка должна быть перегружена с корректным внешним ключом.
    """
    
    new_value = Column(Text)
    """
        Новое значение поля field
    """
    code = Column(String(200))
    """
        Уникальный код подтверждения
    """
    owner_id = Column(Integer, ForeignKey("_rest_users.id", ondelete = "cascade"))
    """
        ID текущего юзера. Для подтверждения юзерских действий. Возможно None
    """
    status = Column(Enum("init", "sended", "finished", "discarded", name = "_rest_confirmate_action_enum"), default = "init")
    """
        статус записи
    """
    created = Column(Integer)
    """
        timestamp создания, в секундах
    """
    
    @property
    def moderated(self):
        """
            Возвращает True или False. 
            
            * True - если статус записи sended и запись еще не истекла
            * False - иначе
            
        """
        
        out = (self.status == "sended")
        if Config()["request.security.confirmation.life_time"]:
            out = out and (time.time() - self.created < Config()["request.security.confirmation.life_time"])
        return out
    
    def generate_code(self):
        out = hashlib.sha256(str(random.randrange(1, 10**100, 1))).hexdigest()
        self.logger.info("Code was generated: %s", out)
        return out
    
    def __init__(self, *a, **k):
        self.logger.info("New db confirmate action generated")
        Base.__init__(self, *a, **k)
        self.created = time.time()
        self.code = self.generate_code()
    
    @classmethod
    def check_confirmation(cls, code, request):
        """
            Выполняет проверку кода, и если все ok, выполняет необходивые изменения
            
            Метод должен выполняться внутри некоторой транзакции
        """
        db_confirm = cls._filter_by(code = code, owner_id = request.userid).first()
        if db_confirm is None or db_confirm.moderated == False:
            return False
        else:
            db_confirmed_object = cls.table._filter_by(id = db_confirm.object_id).update({cls.field:db_confirm.new_value})
            db_confirm.status = "finished"
            return db_confirm
        
    def handle(self, *a, **k):
        """
            Метод должен выполняться внутри транзакции.
            
            Выполняет отправку некоторого запроса на подтверждение. Это может быть:
            
                * Отправка кода по email
                * Отправка СМС
                * etc
        """
        self.status = "sended"

        
    
        
        
    

    
    
    