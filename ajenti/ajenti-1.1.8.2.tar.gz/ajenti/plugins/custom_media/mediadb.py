from ajenti.api import *
from ajenti.plugins import manager

from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

ModelBase = declarative_base()


class Client (ModelBase):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))
    directory_permissions = relationship('ClientDirectoryPermission', backref='client')


class RootDirectory (ModelBase):
    __tablename__ = 'root_directories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    path = Column(String(1023))
    permissions = relationship('ClientDirectoryPermission', backref='directory')


class ClientDirectoryPermission (ModelBase):
    __tablename__ = 'client_directory_permissions'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    directory_id = Column(Integer, ForeignKey('root_directories.id'))


@plugin
class DB (BasePlugin):
    DB_NAME = 'media_library'
    DB_USER = 'root'
    DB_PASSWORD = '123'

    @classmethod
    def instance(cls):
        return cls.get(manager.context)

    def init(self):
        engine = create_engine(
            'mysql+mysqlconnector://%s:%s@localhost'
            % (self.DB_USER, self.DB_PASSWORD),
            echo=False,
            convert_unicode=False,
            encoding='utf-8'
        )
        try:
            engine.execute('CREATE DATABASE IF NOT EXISTS %s' % self.DB_NAME)
        except:
            pass
        engine.execute('USE %s' % self.DB_NAME)
        ModelBase.metadata.create_all(engine)
        self.session = sessionmaker(engine)()

    def list(self, cls):
        return self.session.query(cls).all()

    def create(self, obj):
        self.session.add(obj)
        self.session.commit()

    def commit(self):
        self.session.commit()

    def delete(self, obj):
        self.session.delete(obj)
        self.session.commit()

    def get_client(self, username):
        try:
            return self.session.query(Client).filter(Client.username == username).one()
        except NoResultFound:
            return None

    def get_by_id(self, cls, id):
        return self.session.query(cls).get(id)

