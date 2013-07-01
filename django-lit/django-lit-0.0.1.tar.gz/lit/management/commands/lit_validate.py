from django.core.management.base import NoArgsCommand, CommandError
from lit.models import LitModel,LitBase
from django.utils.importlib import  import_module
from django.db import models
from django.conf import settings

class Command(NoArgsCommand):
    """
    It validates all models that are LitBase subclass.
    """
    help="Validates all models that are LitBase subclass."  
    def handle(self, *args, **options):
        for app_name in settings.INSTALLED_APPS: #controlla tutte le app in INSTALLED_APP
            try:
                import_module('.management', app_name)# Prova ad importare l'applicazione
            except ImportError, exc:
                msg = exc.args[0]
                if not msg.startswith('No module named') or 'management' not in msg: #se non ci riesce lancia eccezione
                    raise        
        for app in models.get_apps(): # cicla tutte le applicazioni
            for m in models.get_models(app): # per ogni modello nell'applicazione corrente
                
                if issubclass(m,LitModel):# se e' subclass di LitModel deve controllare che estende una classe astratta e non conreta
                    for f in m._meta.fields:
                        if f.get_internal_type() == "ForeignKey":
                            if not hasattr(f.rel.to,"LitMeta") or getattr(f.rel.to.LitMeta,"fieldname") != f.name:
                                raise CommandError("Error in %s.%s . LitModel can't have ForeignKey to a No-LitBase model" % (m.__module__,m.__name__))
                    for base in m.__bases__:
                        if issubclass(base,LitModel) and not base._meta.abstract:
                            raise CommandError("Error in %s.%s . LitModel can extend only abstract Model" % (m.__module__,m.__name__))
                elif issubclass(m,LitBase): # se il modello e' sottoclasse di LitBase
                    if not hasattr(m.LitMeta,"litmodel"):  #controlla che abbia il parametro lit nella meta class LitMeta
                        raise CommandError("Error in %s.%s . LitMeta must have field with the name litmodel" % (m.__module__,m.__name__))
                    elif not hasattr(m.LitMeta,"fieldname"): #controlla che abbia il parametro fieldname nella meta class LitMeta
                        raise CommandError("Error in %s.%s . LitMeta must have field with the name fieldname" % (m.__module__,m.__name__))
                    elif not m.LitMeta.litmodel:#controlla che il parametro litmodel non sia nullo nella meta class LitMeta
                        raise CommandError("Error in %s. %s is a LitBase model and it needs a meta class LitMeta." % (m.__module__,m.__name__))
                    elif not hasattr(app,m.LitMeta.litmodel): #controlla che esista il modello definito nel parametro litmodel della meta class LitMeta
                        raise CommandError("Error in %s Model with the name %s doesn't exists." % (m.__module__,m.LitMeta.litmodel))
                    else:
                        litmodel = getattr(app, m.LitMeta.litmodel) #importa il modello ereditato da LitModel
                        if not issubclass(litmodel, LitModel): #controlla che effettivamente sia un LitModel
                            raise CommandError("Error in %s . %s is not a LitModel subclass." % (m.__module__,litmodel.__name__))
                        
                        else: #se LitBase passa la validazione e siamo in un LitModel allora controlla le sue configurazioni
                            foreign_keys = []
                            
                            properties = []
                            for k,v in m.__dict__.items():
                                if type(v) == property:
                                    properties.append(k)
                            
                            for field in litmodel._meta.fields: #per ogni field del litmodel
                                if field.get_internal_type() == "ForeignKey" and m.__name__ == field.rel.to.__name__: 
                                    # se il field e' una FK il nome del modello LitBase == al nome del modello al quale litmodel si riferisce per questo field
                                    foreign_keys.append(field)# aggiunge alla lista questo campo   
                                    if m.LitMeta.fieldname != field.name: 
                                        #se il nome del field definito nella meta class LitMeta != dal nome di questo campo allora lancia eccezione
                                        raise CommandError("Error in %s.%s . LitMeta.fieldname must be like a field's name in %s." % (m.__module__,m.__name__,litmodel.__name__))
                                if field.name in properties:
                                    raise CommandError("Error in %s . %s has the property '%s' with the same name of a %s's attribute." % (m.__module__,m.__name__,field.name,litmodel.__name__))
                            if not foreign_keys:# se la lista e' vuota, significa che il litmodel non ha una FK verso il LitBase
                                raise CommandError("Error in %s . %s has not a field related to %s." % (m.__module__,litmodel.__name__,m.__name__))
        self.stdout.write("0 errors found in all LitBase models\n")