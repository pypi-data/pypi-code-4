from pyinstruments.curvefinder.gui import CurveEditor
from guidata import qapplication as __qapplication
curve_editor = CurveEditor()
_APP = __qapplication()
_APP.exec_()