'''
a module to manage preference
'''
import ConfigParser

from os import path
'''
[guisaxs qt]
defaultdirectory : qlksjdqlksd
recent : qdsqdjqkls
'''


KEYS=['defaultdirectory','recent']
SECTION='guisaxs qt'
MEMORY=5

class prefs():
    
    def __init__(self,filename='guisaxs.ini',section=None):
        self.filename=filename
        if section is None:
            self.section=SECTION
        else:
            self.section=section
        #populate dict wth empty values
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.add_section(self.section)
        for name in KEYS:
            self.parser.set(self.section,name,'')
        
        self.recent=[] #keep in memory the x last files
    
    def fileExist(self,filename=None):
        '''
        return True if preference file exist
        '''
        if filename is not None:
            #change filename
            self.filename=filename
        return path.exists(self.filename)
    
    def save(self,filename=None):
        '''
        save preferences in filename
        '''
        if filename is not None:
            #change filename
            self.filename=filename
        f=open(self.filename,'w')    
        self.parser.write(f)
        f.close()
        #cfgfile.close()
    
    def read(self,filename=None):
        '''
        read preferences from filename
        '''
        if filename is not None:
            #change filename
            self.filename=filename
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(self.filename)
        rec=self.get('recent')
        #print rec
        rec=rec.replace("'",'')
        rec=rec.replace(" ",'')
        rec=rec.split(',')
        #print rec
        self.recent=[]
        for f in rec:
            if f!='':
                self.recent.append(path.normpath(f))#normalize path
    
    def get(self,name,section=None):
        '''
        get the specified preferences
        if the key name don't exist, return None
        '''
        if section is None:
            section=self.section
        if self.parser.has_option(section,name):
            return self.parser.get(section, name)
        else:
            return None
    
    def set(self,name,value,section=None):
        '''
        set the preference
        '''
        if section is None:
            section=self.section
        #print "set prefs : ",name,value,section
        if not self.parser.has_section(section):
            self.parser.add_section(section)
            
        self.parser.set(section, name, value)
        
    def getRecentFiles(self):
        '''
        return the list of recent files
        '''
        return self.recent
    
    def getLastFile(self):
        if len(self.recent)>0:
            return self.recent[0]
        else:
            return None

    def addRecentFile(self,filename):
        '''
        add a recent file
        '''
        filename=path.normpath(filename)
        nl=[filename]
        self.recent=nl+self.recent[:MEMORY-1]
        #print self.recent
        st=str(self.recent)
        st=st.strip('[]\'')
        st=st.replace("'",'')
        self.set('recent',st)
        
        