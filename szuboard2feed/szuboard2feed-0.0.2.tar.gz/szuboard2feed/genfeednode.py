#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from lxml import etree
import times

_ATOM = "http://www.w3.org/2005/Atom"
_TITLE = u"深圳大学公文通"
_AUTHOR = "MarkNV"
_GENERATOR = "szuboard2feed"
_GENERATOR_URL = "http://github.com/marknv/szuboard2feed"


def generate_meta():
    """
    generate meta information of atom.xml, return the root node of etree
    """
    root = etree.Element("feed", xmlns=_ATOM)
    title = etree.Element("title")
    title.text = etree.CDATA(_TITLE)
    updated = etree.Element("updated")
    updated.text = times.format(times.now(), "UTC")
    author = etree.Element("author")
    name = etree.Element("name")
    name.text = etree.CDATA(_AUTHOR)
    generator = etree.Element("generator", uri=_GENERATOR_URL)
    generator.text = _GENERATOR

    root.append(title)
    root.append(updated)
    root.append(author)
    author.append(name)
    root.append(generator)
    return root


def generate_entry(_title, _time, _content, _link):
    """
    generate entry tags of atom.xml and return the entry root node
    """
    entry = etree.Element("entry")
    title = etree.Element("title", type="html")
    title.text = etree.CDATA(_title)
    link = etree.Element("link", href=_link)
    updated = etree.Element("updated")
    updated.text = _time
    content = etree.Element("content", type="html")
    content.text = etree.CDATA(_content)

    entry.append(title)
    entry.append(link)
    entry.append(updated)
    entry.append(content)
    return entry
