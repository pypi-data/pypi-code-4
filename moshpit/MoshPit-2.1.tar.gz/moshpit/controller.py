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
	(host, ssh_port, mosh_port) = split_host(host_string)

	pit = Pit()
	pit.name = pit_name
	pit.host = host
	pit.ssh_port = ssh_port
	pit.mosh_port = mosh_port

	session = get_session()
	session.add(pit)
	session.commit()
	session.close()

	return 0

def update_pit(pit_name, host_string):
	pit = get_pit(pit_name)

	(host, ssh_port, mosh_port) = split_host(host_string)

	pit.host = host
	pit.ssh_port = ssh_port
	pit.mosh_port = mosh_port

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
	return system( "mosh %s --ssh=\"ssh -p %i\" %s" % ('-p %i' % pit.mosh_port if pit.mosh_port else '', pit.ssh_port, pit.host) )

def split_host(host_string):
	split = host_string.split(':')
	if len(split) < 2:
		split.append(22)
	if len(split) < 3:
		split.append(None)

	return (split[0], split[1], split[2])

def migrate():
	pass