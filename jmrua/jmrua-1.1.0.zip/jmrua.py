import os
from platform import system as sisoperativo

"""
This module define my personal develpoment wokplace in transltr-3
"""
_default_workspace = '/home/juanmi/programas/python'
sections = {'default':'.',
            'meet':'meetPython',
            'sharing':'sharingYourCodemeetPython',
            'files':'filesException'}

def __getDefaultPath(operative='LINUX'):
    """Define default values dependiendo del entorno """
    _default_workspace = '/home/juanmi/programas/python/'
    if(operative == 'LINUX'):       
        os.chdir(_default_workspace)
    else:
        _default_workspace = 'C:\\Users\\jmrua\\Documents\\PROGRAMACION\\PYTHON\\prac\\'
        os.chdir(_default_workspace)
    return _default_workspace

def addSection(key,foldername):
    d = os.path.dirname( __getDefaultPath(sisoperativo().upper())+foldername)
    if not os.path.exists(d):
        os.makedirs(d)
    sections[key]=foldername   

def printMenu(operative='LINUX'):
    __getDefaultPath(operative)
    print("SET ENVIRONENT\n\n");
    for key,value in sections.items():        
        print('\t'+key,end='\t -- \t')
        print(value,end='\n')

    print("\n");
    correctChoose = False
    selection = "default"
    sectionselected = sections.get(selection)
    while( not correctChoose):
        selection = input('select your option:')
        correctChoose = selection in sections.keys()
    sectionselected = sections.get(selection)
    __defineWorkingPath(sectionselected)    
    

def __defineWorkingPath(sectionselected):
    """ Set the development workplace in linux"""
    delimiter = '/'
    if(sisoperativo().upper() != 'LINUX'):
        delimiter = '\\'
    os.chdir(__getDefaultPath(sisoperativo().upper())+delimiter+sectionselected)
    print('currently we are here:'+os.getcwd())
    


if __name__== "__main__":
   printMenu(sisoperativo().upper())
