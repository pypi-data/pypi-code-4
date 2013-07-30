from collections import deque

__all__ = ["PeekMessage", "PeekSignal", "GetMessage", "DispatchMessage"]

actorMessageQueue = deque()

def PostMessage(msg):
	actorMessageQueue.append(msg)

def PeekMessage():
	try:
		return actorMessageQueue[0]
	except:
		return None

def GetMessage():
	try:
		return actorMessageQueue.popleft()
	except:
		return None

def PeekSignal():
	try:
		return actorMessageQueue[0][0][2:]
	except:
		return None

def DispatchMessage(tuple):

	fun = getattr(tuple[1][0], tuple[0]).__func__
	fun(*tuple[1], **tuple[2])
	

