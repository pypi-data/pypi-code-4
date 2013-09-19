#!/usr/bin/env python
# -*- coding: utf-8 -*-

def terminal_overlap(firststring, secondstring, limit=15):
    if not (firststring and secondstring):
        return 0
    minl = min(len(firststring), len(secondstring))
    fs  = firststring[-minl:]
    ss = secondstring[:minl]
    offset=0
    if  fs == ss:
        return [(0, 0, minl)]
    best = 0
    length = limit
    while True:
        pattern = fs[-length:]
        found   = ss.find(pattern)
        if found == -1:
            if best>0:
                return [(len(firststring)-best, 0, best)]
            else:
                return []
        length += found
        if fs[-length:] == ss[:length]:
            best = length
            length += 1
            
if __name__=="__main__":
    
    a="GGGCGCGGGCGGNNNNTATATCATATAAA"                                
    b="TATATCATATAAAnnGGGCGCGGGCGG"
    lim = 13
    x,y,l = terminal_overlap(a, b,lim).pop()    
    assert a[x:x+l] == b[y:y+l]
    
    
    a="HavesomeCoCoandCoCo".lower()
    b=        "CoCoandCoCoishere................".lower()
    lim = 11
    x,y,l = terminal_overlap(a, b,lim).pop()    
    assert a[x:x+l] == b[y:y+l]
    
    a="HavesomeCoCoandCoC".lower()
    b=        "CoCoandCoCoishere.".lower()
    lim = 10    
    x,y,l = terminal_overlap(a, b,lim).pop()
    assert a[x:x+l] == b[y:y+l] 
    
    a="HavesomeCoCoandCoCo".lower()
    b=         "oCoandCoCoishere..............................".lower()
    lim = 10
    x,y,l = terminal_overlap(a, b,lim).pop() 
    assert a[x:x+l] == b[y:y+l]

    assert terminal_overlap("atgatcagagtatctatcttgcctcatat".lower(), 
                            "atgatcagagtatctatcttgcctcatat".lower(), 10) == [(0, 0, 29)]

    a="HavesomeCoCoandCoC".lower()
    b="CoCoandCoCoishere.".lower()
    lim = 11   
    assert terminal_overlap(a,b,lim) == []
    
    a="HavesomeCoCoandCoCo".lower() 
    b="oCoandCoCoishere.".lower()
    lim = 11   
    assert terminal_overlap(a,b,lim) == []

                             