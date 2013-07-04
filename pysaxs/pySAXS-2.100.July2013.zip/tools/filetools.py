#__all__=['listFiles','getExtension']
"""
general tools for files manipulation
"""
import numpy
import os
import os.path

def listFiles(paths,file):
    """
    Searches a path for a specified file.
    ListFile("c:\data",*.rgr") return a list with file *.rgr
    """
    import sys
    import os
    import os.path
    import glob
    list=[]
    if file=="" or paths=="":
        print """\
        where (Environment) Filespec
        Searches the paths specified in Environment for all files matching Filespec.
        If Environment is not specified, the system PATH is used.\
        """
    for path in paths.split(";"):
        for match in glob.glob(os.path.join(path, file)):
            list.append(match)
    return list

def getExtension(filename):
    """
    return extension from filename
    """
    #on decoupe la chaine
    l=filename.split(".")
    #l'extension est en fin de liste
    return l[len(l)-1]

def getFilename(filename):
    """
    return name from filename without directory structure
    """
    #on decoupe la chaine
    l=filename.split(os.sep)
    #l'extension est en fin de liste
    return l[len(l)-1]

def fileExist(filename):
    """
    check if a file exist
    """
    return os.path.exists(filename)


def importArray(filename,linestoskip=None,separator='\t',cols=None):
    """
    import a file into a
    numeric float array
    skipping lines beginning by #
    """
    f=open(filename,'r')
    lines=f.readlines()
    datas=[]
    for i in lines[linestoskip:]:
        if i[0]<>'#':
            i=i.replace(separator+'\n','')
            i=i.replace('\n','')
            l=i.split(separator)
            for j in range(len(l)):
                try:
                    l[j]=float(l[j])
                except:
                    l[j]=0.0
            datas.append(l)
    dat=numpy.transpose(numpy.array(datas))
    if cols<>None:
        return dat[:cols]
    else:
        return dat