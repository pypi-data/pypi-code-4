
from pyAMI.client import AMIClient


# set up your arguments for your favorite command
# This is the equivalent of 
# ami cmd TCGetPackageInfo fullPackageName="/External/pyAMI" processingStep="production" project="TagCollector"
# \repositoryName="AtlasOfflineRepository"

argv=[]
# Remember the name of the command must be the first parameter
argv.append("TCGetPackageInfo") 
# The other parameters can be in any order

argv.append("fullPackageName=/External/pyAMI")
argv.append("repositoryName=AtlasOfflineRepository")
# Tell AMI in which catalogue you want to look. TagCollector in this case.
argv.append('project=TagCollector')
argv.append('processingStep=production')

amiClient = AMIClient()

try:
   result=amiClient.execute(argv)
   # Other formats are xml, csv, html 
   # print.result.output('xml')
   #
   # or you can parse the DOM yourself.
   # rowsets = result.dom.getElementsByTagName('rowset')
   # etc.
   
   print result.output()
except Exception, msg:
   error = str(msg) 
   print error
      

