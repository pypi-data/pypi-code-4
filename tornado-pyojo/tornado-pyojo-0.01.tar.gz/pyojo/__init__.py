__version__ = "0.01"
__author__ = [
    "Leandro Brunner <leandrobrunner@gmail.com>",
    "Pyojo Team <contacto@tornado-pyojo.com>"
]
__license__ = "public domain"
__contributors__ = "Ver http://tornado-pyojo.com/cambios"

import tornado.web

def _subApp(parent,child,parenta=""):
	b=[]
	for key in child:
		if type(key[1])==type([]):
			b=b+_subApp(key[0],key[1],parent)
		else:
			new=parenta+parent+key[0]
			if new[-1]=="/":
				new=new[0:-1]
			b.append((new,key[1]))
			#b.append((new+"/",tornado.web.RedirectHandler,{"url":new}))
	return b

def app(a):
	b=[]
	for key in a:
		if type(key[1])==type([]):
			a=a+_subApp(key[0],key[1])
			del(a[a.index(key)])
		else:
			if key[0]!="/" and False:
				if key[0][-1]=="/":
					a.append((key[0][0:-1],key[1]))
				else:
					b.append((key[0]+"/",tornado.web.RedirectHandler,{"url":key[0]}))
	return tornado.web.Application(a+b)

