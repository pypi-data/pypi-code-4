
# $Id: trigger.py 204 2012-07-28 08:52:19Z megido $
__all__ = ['Trigger','TGOP_INSERT','TGOP_UPDATE','TGOP_DELETE','TGEV_AFTER','TGEV_BEFORE']

def allbases_object(obj):
    bases = []
    if obj.__name__ not in ['FormModel','dict','Rules','object','DB']:
        bases.append(obj.__name__)
        
    for o in obj.__bases__:
        if o.__name__  not in ['FormModel','dict','Rules','object','DB']:
            bases.extend(allbases_object(o))
            
    return bases

TGOP_INSERT = 'INSERT'
TGOP_UPDATE = 'UPDATE'
TGOP_DELETE = 'DELETE'
TGEV_AFTER  = 'AFTER'
TGEV_BEFORE = 'BEFORE'

triggers = {
    TGOP_INSERT: {TGEV_AFTER:{},TGEV_BEFORE:{}},
    TGOP_UPDATE: {TGEV_AFTER:{},TGEV_BEFORE:{}},
    TGOP_DELETE: {TGEV_AFTER:{},TGEV_BEFORE:{}}
}

class Trigger():
    @staticmethod
    def connect(sender, functor, tgop, tgev):
        can_attach = True
        for klass in allbases_object(sender):
            if triggers[tgop][tgev].has_key(klass):
                if functor in triggers[tgop][tgev][klass]:
                    can_attach = False
                    
        if can_attach:
            if not triggers[tgop][tgev].has_key(sender.__name__):
                triggers[tgop][tgev][sender.__name__] = []
            triggers[tgop][tgev][sender.__name__].append(functor)
            
    @staticmethod
    def on_trigger(ar, tgop, tgev):
        for klass in allbases_object(ar.__class__):
            if triggers[tgop][tgev].has_key(klass):
                for t in triggers[tgop][tgev][klass]:
                    t(ar, tgev == TGEV_BEFORE)
