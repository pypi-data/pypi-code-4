from datetime import datetime

def l2d( d ):
	return datetime.strptime( d, '%d%m%Y' ) if d else None

def s2d( d ):
	return datetime.strptime( d, '%d%m%y' ) if d else None
