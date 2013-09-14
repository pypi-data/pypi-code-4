##Python Script "creationSeanceIntracursus"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
codeMatiere = REQUEST.form["codeMatiere"]
annee       = REQUEST.form["annee"]
periode     = REQUEST.form["periode"]
intitule    = REQUEST.form["intitule"]
typeseance  = REQUEST.form["typeseance"]
dateseance  = REQUEST.form["dateseance"]
heureseance = REQUEST.form["heureseance"]
dureeseance = REQUEST.form["dureeseance"]

try:
	avecnote = REQUEST.form["avecnote"]
except:
    avecnote = None

# Test whether variable is defined to be None
if avecnote is None:
    avecnote = 0
else:
    avecnote = 1	



try:
	coefficient = REQUEST.form["coefficient"]
except:
    coefficient = None

# Test whether variable is defined to be None
if coefficient is None:
	coefficient = 1.0000
else:
    coefficient = REQUEST.form["coefficient"]





try:
    publiable = REQUEST.form["publiable"]
except:
    publiable = None

# Test whether variable is defined to be None
if publiable is None:
    publiable = 0
else:
    publiable = 1	

retour = context.verifCreationSeanceIntracursus(codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient)
REQUEST.RESPONSE.redirect("%s/@@jalon-intracursus?message=%s" % (context.aq_parent.absolute_url(), retour))

