#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Wed 18 May 09:28:44 2011 

"""The 3D Mask Attack Database for face spoofing consists of 255 color and depth videos of
3D mask attack attempts to 17 clients, taken in three different sessions under ideal conditions. 
This database was produced at the Idiap Research Institute, in Switzerland.

If you use this database in your publication, please cite the following paper
on your references:

.. code-block:: sh
    TODO:UPDATE
    
  @INPROCEEDINGS{Chingovska_BIOSIG-2012,
    author = {Chingovska, Ivana and Anjos, Andr\\'e and Marcel, S\\'ebastien},
    keywords = {biometric, Counter-Measures, Local Binary Patterns, Spoofing Attacks},
    month = september,
    title = {On the Effectiveness of Local Binary Patterns in Face Anti-spoofing},
    journal = {IEEE BIOSIG 2012},
    year = {2012},
  }
"""

from .query import Database
from .models import Client, File, Protocol

__all__ = dir()
