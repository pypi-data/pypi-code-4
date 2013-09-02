from datetime import datetime

def l2d( d ):
	return datetime.strptime( d, '%d%m%Y' ) if d else None

def s2d( d ):
	return datetime.strptime( d, '%d%m%y' ) if d else None

def ssn2dob( ssn ):
	century = int( ssn[-1] )
	century = 20 - 11%(century+1)
	dob_str = ssn[:4] + str(century) + ssn[4:6]
	return l2d( dob_str )