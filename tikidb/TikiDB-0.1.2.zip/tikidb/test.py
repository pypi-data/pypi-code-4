import transaction, os
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from persistent  import Persistent
from BTrees.IOBTree import IOBTree,IOTreeSet,IOSet
from BTrees.OOBTree import OOBTree,OOTreeSet,OOSet
import ZODB
import ZODB.FileStorage
from  TikiDB import Record


storage = ZODB.FileStorage.FileStorage('dict.zodb')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
d = {1:1,2:2,3:3,4:4,5:5}
for i in range(0,1000):
    data = d
    root[i]=data
transaction.commit()
db.close()
print '1000 dict = ',os.path.getsize('./dict.zodb')," Bytes"


storage = ZODB.FileStorage.FileStorage('PersistentMapping.zodb')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
d = {1:1,2:2,3:3,4:4,5:5}
for i in range(0,1000):
    data = PersistentMapping(d)
    root[i]=data
transaction.commit()
db.close()
print '1000 PersistentMappings = ',os.path.getsize('./PersistentMapping.zodb')," Bytes"

storage = ZODB.FileStorage.FileStorage('OOBTree.zodb')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
d = {1:1,2:2,3:3,4:4,5:5}
for i in range(0,1000):
    data = OOBTree(d)
    root[i]=data
transaction.commit()
db.close()
print '1000 OOBTrees = ',os.path.getsize('./OOBTRee.zodb')," Bytes"

storage = ZODB.FileStorage.FileStorage('records.zodb')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
d = {1:1,2:2,3:3,4:4,5:5}
for i in range(0,1000):
    data = Record()
    root[i]=data
transaction.commit()
db.close()
print '1000 records = ',os.path.getsize('./records.zodb')," Bytes"


storage = ZODB.FileStorage.FileStorage('IOBTree.zodb')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
d = {1:1,2:2,3:3,4:4,5:5}
for i in range(0,1000):
    data = IOBTree(d)
    root[i]=data
transaction.commit()
db.close()
print '1000 IOBTrees = ',os.path.getsize('./IOBTree.zodb')," Bytes"
