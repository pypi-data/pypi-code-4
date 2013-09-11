import commandeer

def test_command(boole=True, number=0, value=''):
	print("boole={}, number={}, value={}".format(repr(boole), repr(number), repr(value)))
	
if __name__ == '__main__':
	commandeer.cli()