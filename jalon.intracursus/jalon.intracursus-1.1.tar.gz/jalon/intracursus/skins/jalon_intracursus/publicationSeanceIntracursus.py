##Python Script "publicationSeanceIntracursus"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
codematiere = REQUEST.form["codematiere"]
intitule = REQUEST.form["intitule"]
publiable = REQUEST.form["publiable"]

retour = context.verifPublicationSeanceIntracursus(codematiere, intitule, publiable)

REQUEST.RESPONSE.redirect("%s/@@jalon-intracursus?message=%s" % (context.aq_parent.absolute_url(), retour))
