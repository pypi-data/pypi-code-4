from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from persistent  import Persistent
from BTrees.IOBTree import IOBTree,IOTreeSet,IOSet
from BTrees.OOBTree import OOBTree,OOTreeSet,OOSet


class TikiWareError(Exception):
    def __init__(self,message):
        self.message=message
        self.args = (message,)
    def __str__(self):
        return repr(self.message)

class Container(Persistent):
    """
    data container for root. override validate to use validataion

    """
    def __init__(self):
        self.data = IOBTree()
        self.uniqueFields = OOTreeSet()#tuple of key name or names that must
                                        #be unique for each record stored or
                                        #it will be considered the same record
                                        
        self.uniqueRecords = OOTreeSet()#tuple of values of the keys from
                                         #unique_fields to quickly verify
                                         #unique data set
        
        self.index_list = OOTreeSet() #string values of the names of indexes
                                      #that can be associated to data values
        
        self.recordDefinition = IOBTree()#has all record definition versions
                                          #highest key is current.  keeps old
                                          #versions to fix issues
        
        super(Container,self).__init__()

    def setRecordDefinition(self,obj):
        """
        obj is a ZODB persistent object.  inserts a new object every time the
        method is run.  most current is the highest integer. old versions are
        kept to fix issues with records in the container.

        """
        err =False
        try:
            if len(self.recordDefinition):
                key = self.recordDefinition.maxKey() + 1
            else:
                key = 1
            print key
            if isinstance(obj,(Persistent,)):
                ok = self.recordDefinition.insert(key,obj)
                print 'ok = ',ok
                if not ok:
                    err = TikiWareError('Unable to add record definition')
            else:
                err = TikiWareError('%s object is not instance of Persistent '%obj.__class__)
            if err:
                raise err
        except Exception as e:
            raise e
        return
    
    def getRecordObject(self):
        """
        get the current record object.  used to create new records

        """
        if len(self.recordDefinition):
            obj = copy.deepcopy(self.recordDefinition[self.recordDefinition.maxKey()])
            return obj
        err = TikiWareError('No current record definition')
        err.args = ("No current record definition",)
        raise err

    def setUniqueFields(self,field_list,override=False):
        """
        set the list of fields that must be a unique combination per record
        field_list must be list or tuple and must not have its order changed

        """
        field_list = OOTreeSet(field_list)
        if len(self.uniqueFields) and  overrride:
            #unique fields have been updated and the uniqueRecords index
            #needs to be rebuilt after the unique file list has been updated.
            self.uniqueFields = field_list
            pass #<--- do update to uniqueRecords
            return
        elif len(self.uniqueFields):
            err = TikiWareError('unique field list exists. to update set override to True')
            raise err
        self.uniqueFields = field_list
        return
        
            
    def getNextID(self,obj_name):
        """
        get the next object ID from a data container
        
        :param obj_name: the name of the container
        :type obj_name: string

        :returns: the next integer ID for a container

        """
        next_id = self.data.maxKey() + 1
        return next_id

    def indexAdd(self,index_name):
        """
        add index name to  index_list.  return false for exists or fail
        NOTE: does not add the index to the database
        """
        err = self.index_list.add(index_name)
        if err:
            return '%s index exists'%index_name
        return
    
    def indexRemove(self,index_name):
        """
        remove an index from the index_list. return false for no exist or fail
        NOTE: does not remove the index from the database

        """
        err = self.index_list.has_key(index_name)
        if err:
            return '%s index does not exist'%index_name
        self.index_list.remove(index_name)
        return
        
        
    def addRecord(self,data,update=False):
        """
        add data to the container, if update is true, replace

        """
        pass

    def verifyUnique(self,fields):
        """
        verify a record is unique in a container for the fields
        in the uniqueFields set

        """
        pass
    
    def verifyRequiredFields(self,data):
        key = self.recordDefinition.maxKey()
        print key
        
        if hasattr(self.recordDefinition[key],'__dict__'):
            required_fields = dict(self.recordDefinition[key].__dict__)
        else:
            required_fields = dict(self.recordDefinition[key])
        print 'needed fields =', required_fields
        for k,v in data.iteritems():
            value = required_fields.pop(k,None)
        print 'rk = ',required_fields
        if required_fields:
            err = TikiWareError('Record Error: required fields not found')
            return err
        return
    
    def validate(self,data):
        """
        override in subclass to implement record validataion using
        super(sub_class,self).validate(self)
        if error return a value or error

        """

        #verify all fields exist that are in the recordDefinition
        missing_err = None
        #verify that record's unique field set does not exist in container
        
        unique_err = self.verifyUnique
        if unique_err and missing_err:
            err = TikiWareError('record is not unique and has missing fields')
            raise
        elif unique_err:
            err = TikiWareError('record is not unique')
            raise
        elif missing_err:
            err = TikiWareError('record is missing required fields')
            raise
        print 'i am base'


if __name__=='__main__':
    c = Container()
    rd = OOBTree({1:None,2:None})
    good_record = OOBTree({1:'1',2:'2'})
    bad_record = OOBTree({1:'1'})
    c.setRecordDefinition(rd)
    
