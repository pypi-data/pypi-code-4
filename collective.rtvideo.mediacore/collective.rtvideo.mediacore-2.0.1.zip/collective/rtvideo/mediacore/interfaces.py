# -*- coding: utf-8 -*-
from zope.interface import Interface


class IUseJWPlayer(Interface):
    """
    @author: lucabel
    @description: implement this class just to have the jwplayer javacript
    in the page head
    """

class IUseMediacorePlayer(Interface):
    """
    @author: lucabel
    @description: implement this class to simply getthe player from mediacore
    """