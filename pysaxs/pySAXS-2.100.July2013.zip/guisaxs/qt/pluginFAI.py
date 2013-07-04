from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgQtFAI

classlist=['pluginFAI']

class pluginFAI(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="Radial Averaging"
    
    def execute(self):
        #get the preferences
        parameterfile=self.parent.pref.get("parameterfile",'pyFAI')
        ouputdir=self.parent.pref.get('outputdir','pyFAI')
        #display the FAI dialog box
        self.dlgFAI=dlgQtFAI.FAIDialog(self.parent,parameterfile,ouputdir)
        self.dlgFAI.show()
        