##Python Script "listerSeanceIntracursus"
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

retour = context.verifListSeanceIntracursus(codeMatiere)

REQUEST.RESPONSE.redirect("%s/@@jalon-intracursus?message=%s" % (context.aq_parent.absolute_url(), retour))
