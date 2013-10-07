"""Observable list class"""
from pydispatch.dispatcher import send
class OList( list ):
	"""List sub-class which can generate pydispatch events on changes"""
	def append( self, value ):
		"""Append a value and send a message"""
		super( OList,self ).append( value )
		send( 'new', self, value=value)
		return value 
	def __setitem__( self, index, value ):
		"""Set a value and send a message"""
		send( 'del', self, value=self[index] )
		super( OList,self ).__setitem__( index, value )
		send( 'new', self, value=value)
		return value 
	def __setslice__(self, slice, iterable ):
		"""Set values and send messages"""
		for current in self.__getslice__( slice ):
			send( 'del', self, value=current )
		values = list(iterable)
		super(OList,self).__setslice__( slice, values )
		for value in values:
			send( 'new', self, value=value )
		return values 

if __name__ == "__main__":
	from pydispatch.dispatcher import connect
	o = OList()
	out = []
	def on_new( signal, value ):
		out.append( (signal,value) )
	connect( on_new, sender=o )
	o.append( 'this' )
	assert out == [('new','this')]
	del out[:]

	o[0:2] = [ 'those','them' ]
	assert out == [('del','this'),('new','those'),('new','them')]
	del out[:]
	
	o[1] = 'that'
	assert out == [('del','those'),('new','that')]
