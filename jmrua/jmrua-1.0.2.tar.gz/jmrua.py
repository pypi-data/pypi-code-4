import os

"""
This module define my personal develpoment wokplace in transltr-3
"""
_default_workspace = '/home/juanmi/programas/python'
sections = {'default':'.',
            'meet':'meetPython',
            'sharing':'sharingYourCodemeetPython',
            'files':'filesException',
            'persistence':'persistence'}

def __init(operative='LINUX'):
    """Define default values dependiendo del entorno """
    if(os == 'LINUX'):
        _default_workspace = '/home/juanmi/programas/python'
        os.chdir(_default_workspace)
    
    
    
                

def printMenu():
    __init()
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
    os.chdir(_default_workspace+'/'+sectionselected)
    print('currently we are here:'+os.getcwd())
    


if __name__== "__main__":
   printMenu()
