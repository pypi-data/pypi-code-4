def setupVarious(context):
    if context.readDataFile('collective.languagemovefolders_various.txt') is None:
        return
    site = context.getSite()
