

'''

decryptPass.py
==========

Desc: code refer to Rafael Arana 's http://techtapas.blogspot.com.au/2011/05/how-to-decrypt-weblogic-passwords-with.html

Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import os
import weblogic.security.internal.SerializedSystemIni
import weblogic.security.internal.encryption.ClearOrEncryptedService

def usage():
    print "Usage:"
    print "wlst.sh decryptPass.py <domainhome> <encryptpass> "

def decrypt(domainhome, encryptpass):
    domainHomePath = os.path.abspath(domainhome)
    encryption = weblogic.security.internal.SerializedSystemIni.getEncryptionService(domainHomePath)
    wlces = weblogic.security.internal.encryption.ClearOrEncryptedService(encryption)
    plainpwd = wlces.decrypt(encryptpass)
    print plainpwd

try:
     decrypt(sys.argv[1], sys.argv[2])
except:
    print 'NA'

