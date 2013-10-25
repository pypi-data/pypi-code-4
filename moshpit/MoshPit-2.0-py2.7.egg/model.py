from os import path
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def get_engine():
	db_path = path.join( path.expanduser("~"), '.moshpit.db' )
	return create_engine('sqlite:///%s' % db_path)

def get_session():
	engine = get_engine()
	Session = sessionmaker(bind=engine)
	return Session()

class Pit1(Base):
	__tablename__ = 'pits'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	host = Column(String)
	port = Column(Integer)

	def __repr__(self):
		return "%s    %s:%i" % (self.name, self.host, self.port)

class Pit(Base):
	__tablename__ = 'pits2'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	host = Column(String)
	ssh_port = Column(Integer)
	mosh_port = Column(Integer)

	def __repr__(self):
		return "%s    %s:%i%s" % (self.name, self.host, self.ssh_port, ':%i' % self.mosh_port if self.mosh_port else '')

Pit.metadata.create_all(get_engine())