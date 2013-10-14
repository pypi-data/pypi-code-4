##Python Script "creationPresenceIntracursus"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
numero       = REQUEST.form["numero"]
nom          = REQUEST.form["nom"]
prenom       = REQUEST.form["prenom"]
idseance     = REQUEST.form["idseance"]
statut       = REQUEST.form["statut"]
note         = REQUEST.form["note"]
appreciation = REQUEST.form["appreciation"]
datepresence = REQUEST.form["datepresence"]

retour = context.verifCreationPresenceIntracursus(numero, nom, prenom, idseance, statut, note, appreciation, datepresence)

REQUEST.RESPONSE.redirect("%s/@@jalon-intracursus?message=%s" % (context.aq_parent.absolute_url(), retour))
