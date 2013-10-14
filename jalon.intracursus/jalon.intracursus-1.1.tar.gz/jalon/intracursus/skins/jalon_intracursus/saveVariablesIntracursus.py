##Python Script "saveVariablesIntracursus"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
intracursus = {"urlConnexion":      REQUEST.form["urlConnexion"],
               "loginConnexion":    REQUEST.form["loginConnexion"],
               "passwordConnexion": REQUEST.form["passwordConnexion"]}

retour = context.setVariablesIntracursus(intracursus)

REQUEST.RESPONSE.redirect("%s/@@jalon-intracursus?message=%s" % (context.aq_parent.absolute_url(), retour))
