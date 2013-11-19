'''
Created on Nov 1, 2013

@author: Jose Borreguero
'''

from logger import vlog, tr
from distutils.version import LooseVersion

class Parser(object):
    '''
    Determines which parser to use in order to read mdend
    '''


    def __init__(self, mfile):
        '''
        Constructor
        '''
        self._file=mfile
        self._versions = [LooseVersion(x) for x in ('12',)]     
        self._version = self.detectVersion(mfile)
        
    def detectVersion(self, mfile):
        '''Find parser with latest version that will read the file 
        '''
        try:
            pf=open(mfile)
        except IOError, e:
            vlog.error(e)
            raise
        check=False
        for version in self._versions:
            if version==LooseVersion('12'):
                '''Parser for amber 12 and below
                    L0  Nsteps           time(ps)         Etot             EKinetic        
                    ...
                '''
                line=pf.readline()
                if line[:3]=='L0 ':
                    check=True
                    vlog.info( 'Using version {}'.format(str(version)) )
                else:
                    pf.seek(0)
            if check:
                return version
        if not check: 
            vlog.error('Could not find a valid version!')
            raise


    def parse(self):
        '''Parse the mdend file into a list of fields and a list of contents'''
        if self._version==LooseVersion('12'):
            '''Parser for amber 12 and below
                L0  Nsteps           time(ps)         Etot             EKinetic        
                ...
            '''
            def readFields(mfile):
                '''Load the names of the fields, and the number of lines per chunk'''
                pf=open(mfile)
                line=pf.readline()
                ilines=0
                imax=-1
                fields=[]
                while True:
                    items=line.split()
                    i=int(items[0][1:]) #L0
                    if i<imax: break
                    imax=i
                    ilines+=1
                    fields += items[1:]
                    line=pf.readline()
                pf.close()
                return ilines, fields
            
            def readEntry(pf, linesperentry):
                '''Read one entry'''
                entry=[]
                for _ in range(linesperentry):
                    entry += [ float(value) for value in pf.readline().split()[1:] ]
                return entry
            
            def readContents(mfile, linesperentry, nfields):
                '''Read all entries'''
                pf = open(mfile)
                contents = []
                for _ in range(nfields): contents.append([])
                for _ in range(linesperentry): pf.readline() # bypass header
                entry = readEntry(pf, linesperentry)  # read first entry
                while entry:
                    for i,value in list(enumerate(entry)):
                            contents[i].append(value) 
                    entry = readEntry(pf, linesperentry)
                pf.close()
                return contents
                
            self._linesperentry, self._fields = readFields(self._file)
            self._contents=readContents(self._file, self._linesperentry, len(self._fields))
    
    def getValues(self, field):
        try:
            i=self._fields.index(field)
        except:
            vlog.error('Field {} not found in list of fields'.format(field))
            raise
        return self._contents[i]
    
    def getFields(self):
        return self._fields

            
            
            
        
        