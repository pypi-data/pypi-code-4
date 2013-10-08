def funcrandom():
	global B
	import random
	B=random.randint(1,10)

def captura():
	global A		
	A= int(raw_input("Ingrese Numero: "))
	
def Fnombre():
	global nom
	nom = raw_input("Ingrese Su Nombre: ")
	
	print "\nBienvenido!!!!..... " + str(nom.upper()) +"\n"

def creartxt():
    archi=open('datos.txt','a')
    archi.close()

creartxt()
	
def grabartxt():
    archi=open('datos.txt','a')
    archi.write('Jugador: | '+ str(nom)+' | intentos: | '+ str(cont) +' | numero adivinado: | '+str(B)+' | \n')    
    archi.close()

def leertxt():	
    archi=open('datos.txt','r')
    linea=archi.readline()
    while linea!="":
        print linea
        linea=archi.readline()
		
def adivina():
	global cont
	cont=1
	leertxt()
	salir = False
	Fnombre()
	funcrandom()
	BB=int(B)	
	while not salir:
		captura()		
		if A == B :
			print "AS ADIVINADO EL NUMERO!!!!! : " + str(BB)
			salir = True
			print "as adivinado el numero en "+ str(cont) + " intentos"
			
			grabartxt()				
		else:
			if A>B:
				print "EL NUMERO ES MENOR \n"	
				cont+=1				
			else:
				print "EL NUMERO ES MAYOR \n"				
				cont+=1
				
print "PROGRAMA QUE SIRVE PARA ADIVINAR UN NUMERO ALEATORIO \n"

adivina()
