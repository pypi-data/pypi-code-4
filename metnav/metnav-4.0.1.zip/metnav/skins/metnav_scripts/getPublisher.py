##parameters=publisher=''
##title=get Publisher Name from  vcard

acadFn      = str(publisher).split("\n")[3]
acadName    = acadFn.split(":")[1]

return acadName
