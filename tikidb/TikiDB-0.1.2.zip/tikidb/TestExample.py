from TikiDB import DB, Record, Container

class Cooks(Container):
    def __init_(self):
        super(Cooks,self).__init()

        
db = DB('test2')
cooks = Cooks()
cook = Record()
cook.name = 'Bobby'
cook.recipes =['apple','water']
db.root['cooks'] = cooks
db.root['cooks'].addRecord(cook)
