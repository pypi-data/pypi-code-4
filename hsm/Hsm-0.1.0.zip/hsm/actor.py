import default_logger
import types
from runtime import PostMessage as Post

__all__ = [ "ActorTopState", "initialState", "MissingInitialStateError", "NotHsmStateError" ]

def CreateMessageSender(fun, name, handlerName):

	def PostMessage(*args, **kwargs):
		self = args[0] 
		self._log.trace("(%s : %s) about to send message ('%s' args:%s kwargs:%s) ", id(self), self.__class__.__name__, name, str(args), str(kwargs), )		
		Post( (handlerName, args, kwargs) )

	return PostMessage

def CreateMessageReceiver(fun, name):
	
	def ReceiveMessage(*args, **kwargs):
		self = args[0] 
		self._log.trace("(%s : %s) about to receive message ('%s' args:%s kwargs:%s) ", id(self), self.__class__.__name__, name, str(args), str(kwargs), )		
		return fun(*args, **kwargs)

	return ReceiveMessage

class MissingInitialStateError(Exception):

	def __init__(self, state):
		self._state = state

	def __str__(self):
		return "%s is missing the initial state. Use @initialState to mark the initial state" % (self._state.__name__)

class NotHsmStateError(Exception):

	def __init__(self, state):
		self._state = state

	def __str__(self):
		return "@initialState can only by applied to a child class of HsmTopState. '%s' is not child of HsmTopState" % (self._state.__name__)

def EmptyFunction(self):
	pass

class ActorMetaClass(type):
	
	def __new__(meta, name, bases, dct):
		return type.__new__(meta, name, bases, dct)

	def __init__(cls, name, bases, dct):
		type.__init__(cls, name, bases, dct)
		cls.__initial_state__ = None
		if not dct.has_key("_exit"):
			setattr(cls, "_exit", types.MethodType(EmptyFunction, None, cls) ) 
		if not dct.has_key("_enter"):
			setattr(cls, "_enter", types.MethodType(EmptyFunction, None, cls) )
		for (k,v) in dct.items():
			if k.startswith("send"):
				raise ReservedNameError(name, k, "send prefix is reserved to send messages")
			if k.startswith("on"):
				msgName = k[2:]
				if not msgName[:1].isupper():
					raise NameError(name, k, "'on' prefix must be followed by a capital case letter")				
				senderName = "send" + msgName
				receiver = CreateMessageReceiver(v, msgName)
				sender   = CreateMessageSender(receiver, msgName, k)
				setattr(cls, k , receiver)
				setattr(cls, senderName , sender)

	def __call__(cls, *args, **kwds):

		instance = type.__call__(cls, *args, **kwds)
	
		initialState = instance.__class__.__initial_state__
		if initialState == None:
			raise MissingInitialStateError(cls)

		if not hasattr(instance, "_logger"):
			instance._log = default_logger
		
		instance._log.trace( "(%s : <>): about to enter state (%s)", id(instance), instance.__class__.__name__ )
		instance._enter()
		while initialState is not None:
			instance._log.trace( "(%s : %s): about to enter state (%s)", id(instance), instance.__class__.__name__, initialState.__name__ )
			instance.__class__ = initialState
			instance._enter()
			initialState = initialState.__initial_state__

		instance._initialState = cls
		return instance

def GetParentState(st):
	return st.__bases__[0]

def GetInitialState(st):
	return st.__class__.__initial_State__

class ActorTopState(object):
	__metaclass__ = ActorMetaClass

	def _enter(self):
		pass

	def _exit(self):
		pass

	def onFini(self):
		while True:
			self._log.trace( "(%s : %s): about to exit state", id(self), self.__class__.__name__,)
			self._exit()
			parentState = self.__class__.__bases__[0]
			if parentState != ActorTopState:
				self.__class__ = parentState		
				continue
			break
			

	def transition(self, state):
		outState = self.__class__
		inState  = state
		left  = outState
		right = inState
		if left == right:
			self._log.warn("transition to current state has no effect")
			return
		assert left != ActorTopState
		assert right != ActorTopState
		
		while left != ActorTopState and right != left:
			left = left.__bases__[0]
			right = inState
			while right != ActorTopState and right != left:
				right = right.__bases__[0]

		assert left == right			
		
		#Execute Exits		 
		while self.__class__ != left:
			self._log.trace( "(%s : %s): about to exit state", id(self), self.__class__.__name__,)
			self._exit()
			self.__class__ = self.__class__.__bases__[0]

		### Fix Start ....		
		# Left = Right --> Lowest Common Ancestor
		assert self.__class__ == left
		if inState != self.__class__:
			head =  inState.__bases__[0]
			enterTrail = []
			if head != ActorTopState:
				while head != left:
					enterTrail.append(head)
					head = head.__bases__[0]

			while enterTrail:
				head = enterTrail.pop()
				self._log.trace( "(%s : %s): about to enter state (%s)", id(self), self.__class__.__name__,  head.__name__ )
				self.__class__ = head
				self._enter()

			#Enter target state
			self._log.trace( "(%s : %s): about to enter state (%s)", id(self), self.__class__.__name__, inState.__name__)
			self.__class__ = inState
			self._enter()

		### Fix End ....		

		



		#Drill down
		nextState = self.__class__.__initial_state__
		while nextState is not None:
			self._log.trace( "(%s : %s): about to enter state (%s)", 
				id(self), 
				self.__class__.__name__,  
				nextState.__name__ )
			self.__class__ = nextState
			self._enter()
			nextState = nextState.__initial_state__

	
def initialState(state):
	parent = state.__bases__[0]
	if not issubclass(parent, ActorTopState):
		raise NotActorStateError(state)
	if parent != ActorTopState:
		parent.__initial_state__ = state
	return state	
