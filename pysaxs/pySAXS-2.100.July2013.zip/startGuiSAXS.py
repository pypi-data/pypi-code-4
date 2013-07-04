'''
execute this file for opening guiSAXS (the graphic user interface for pySAXS)
'''
from pySAXS.guisaxs.wx import GuiSAXS
if __name__== '__main__':
    app = GuiSAXS.wx.App()
    frame = GuiSAXS.GuiSAXS(None, 1)
    app.MainLoop()