# -*- coding: utf-8 -*-
"""
Objet de compositions à partir des éléments
"""
# -*- coding: utf-8 -*-
"""
Parser de backends
"""
from Sveetchies.gantt.readers import XmlReader
from Sveetchies.gantt.png.composers import ScheduleSceneComposer
from Sveetchies.gantt.demos import DEMOS_OUTPUT_PATH

x = XmlReader()
styles = x.get_styles("./styles.xml")
backend = x.get_backend("./demo.xml")

ssd = ScheduleSceneComposer(backend, opts=styles)
print ssd.__repr__()
diag_scene = ssd.draw()
#
diag_scene.save(DEMOS_OUTPUT_PATH%"diagram_from_xml_backend.png", "PNG")
