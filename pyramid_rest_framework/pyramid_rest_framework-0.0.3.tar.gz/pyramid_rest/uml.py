#-*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph
"""
Модуль, использующийся для создания и документирования UML диаграммы текущей БД
"""

def doc_uml(Base, path):
    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(metadata=Base.metadata,
       show_datatypes=False, # The image would get nasty big if we'd show the datatypes
       show_indexes=False, # ditto for indexes
       rankdir='LR', # From left to right (instead of top to bottom)
       concentrate=False # Don't try to join the relation lines together
    )
    graph.write_png(path) # write out the file