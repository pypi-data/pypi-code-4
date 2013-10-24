from os import system
from sqlalchemy.orm.exc import NoResultFound
from model import Pit, get_session

def get_pit(pit_name):
	session = get_session()
	try:
		pit = session.query(Pit).filter(Pit.name == pit_name).one()
		session.close()
		return pit
	except NoResultFound, e:
		session.close()
		return None

def create_pit(pit_name, host_string):
	split_host = host_string.split(':')
	if len(split_host) < 2:
		split_host.append(22)

	pit = Pit()
	pit.name = pit_name
	pit.host = split_host[0]
	pit.port = split_host[1]

	session = get_session()
	session.add(pit)
	session.commit()
	session.close()

	return 0

def update_pit(pit_name, host_string):
	pit = get_pit(pit_name)

	split_host = host_string.split(':')
	if len(split_host) < 2:
		split_host.append(22)

	pit.host = split_host[0]
	pit.port = split_host[1]

	session = get_session()
	session.add(pit)
	session.commit()
	session.close()

	return 0

def remove_pit(pit_name):
	pit = get_pit(pit_name)

	session = get_session()
	session.delete(pit)
	session.commit()
	session.close()

	return 0

def list_pits():
	session = get_session()

	for pit in session.query(Pit).all():
		print pit

	session.close()
	return 0

def pit(pit_name):
	pit = get_pit(pit_name)
	return system( "mosh --ssh=\"ssh -p %i\" %s" % (pit.port, pit.host) )