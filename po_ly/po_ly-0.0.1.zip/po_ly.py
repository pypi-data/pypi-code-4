import math
def intro():
    print("rec(width,length),sq(length),tri(fllen,hei)")
    print("dia(onelen,hei),para(fllen,hei),ladder(uplen,downlen,hei)")
    print("circle(r),fan(r,angle)@all number is *.*@")
def rec(width,length):
    if str(type(width))=="<class 'float'>" and str(type(length))=="<class 'float'>":
        cmx=width*length
        return cmx
def sq(length):
    if str(type(length))=="<class 'float'>":
        cmx=math.pow(length,2)
        return cmx
def tri(fllength,height):
    if str(type(fllength))=="<class 'float'>" and str(type(height))=="<class 'float'>":
        cmx=fllength*height/2
        return cmx
def dia(onelength,height):
    if str(type(onelength))=="<class 'float'>" and str(type(height))=="<class 'float'>":
        cmx=onelength*height
        return cmx
def para(fllength,height):
    if str(type(fllength))=="<class 'float'>" and str(type(height))=="<class 'float'>":
        cmx=fllength*height
        return cmx
def ladder(uplength,downlength,height):
    if (str(type(uplength))=="<class 'float'>" and str(type(downlength))=="<class 'float'>") and str(type(height))=="<class 'float'>":
        cmx=(uplength+downlength)*height/2
        return cmx
def circle(r):
    if str(type(r))=="<class 'float'>":
        cmx=r*r*math.pi
        return cmx
def fan(r,angle):
    if str(type(r))=="<class 'float'>" and str(type(angle))=="<class 'float'>":
        cmx=r*r*math.pi*(angle/360)
        return cmx
