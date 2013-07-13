##############################################################################
# File:            epubC.py
# Description:     Classes for editing an epub file.
# Authors:         Awad Mackie <firesock.serwalek@gmail.com>
# Date:            02-07-2010
# Copyright:       (c) 2010 firesock serwalek
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

##############################################################################/

"""
This modules provides classes to create a EPUB file from scratch given data.

See documentation on class Epub.
"""

import tempfile, shutil, os, zipfile, hashlib, datetime
from lxml.builder import ElementMaker
from lxml import etree

DCMI = "http://purl.org/dc/elements/1.1/"
OPF = "http://www.idpf.org/2007/opf"
NCX = "http://www.daisy.org/z3986/2005/ncx/"

class Epub(object):
	"""
	Class is used to create epub files, writing all necessary XML and contents pages.

	Example of use:
	import epubC
	
	ep = epubC.Epub("Title", "Author", "ID")
	
	As specifed, ID should be a unique identifier such as an ISBN. Attribs are set on the object
	for easy change.
	
	ep.add("content.html", "application/xhtml+xml", io.StringIO(html), "Chapter 1")

	Arcname is the internal name incase any other files reference it. html contents must be
	valid XHTML, so set media type accordingly. data is a stream out of an html string in memory,
	but can be data of any type, even binary.
	Title is the Chapter/Section name.
	
	ep.add("test.css", "text/css", io.StringIO(css))

	If the title is omitted or None, it assumes that it is not in the linear reading order
	and only adds it to the file.
	
	ep.write("test.epub")

	Creates the final file in name specified. No extensions are added, so specify full path.
	
	ep.close()

	Frees up temporary files made in the process. Call this unless you want your storage
	littered with files.

	Context managers are also supported, so:
	with epubC.Epub("Title", "Author", "ID") as ep:
		ep.add("content.html", "application/xhtml+xml",	io.StringIO(html), "Chapter 1")
		ep.write("test.epub")

	In addition to attributes specified above, additional metadata attributes are supported:

    - subject, description, publisher, contributor, date, type, format, source, relation, coverage, rights

	Set them on the Epub object to write as OPF metadata. Please refer to the spec for further details.
	Lists will be written as multiple tags and dates converted from Python datetime.date objects.	
	"""

	_uid_id_str = "bookid"

	_metadata = dict(
		title = ["title", {}],
		author = ["creator", {"{%s}role" % OPF : "aut"}],
		uid = ["identifier", {"id" : _uid_id_str}],
		language = ["language", {}],
		subject = ["subject", {}],
		description = ["description", {}],
		publisher = ["publisher", {}],
		contributor = ["contributor", {}],
		date = ["date", {}],
		type = ["type", {}],
		format = ["format", {}],
		source = ["source", {}],
		relation = ["relation", {}],
		coverage = ["coverage", {}],
		rights = ["rights", {}],
		)

	def _dcmi_taglist(self, attr_vals, tag, attribs):
		"""Internal: get tags for single supported DCMI tag"""
		if not isinstance(attr_vals, list):
			attr_vals = [attr_vals]

		taglist = []
		for value in attr_vals:
			#Just run through some common transformations
			if isinstance(value, datetime.date):
				value = value.isoformat()

			taglist.append(getattr(self._DCMI, tag)(value, **attribs))

		return taglist

	def _dcmi_tags(self):
		"""Internal: get list of all set DCMI tags"""
		tags = []
		
		for py_attrib, (tag, attribs) in self._metadata.items():
			attr_val = getattr(self, py_attrib, None)
			if attr_val is not None:
				tags.extend(self._dcmi_taglist(attr_val, tag, attribs))

		return tags
				
	
	def _standard_setup(self):
		"""Internal function to create standard files at the beginning."""
		self._meta = os.path.abspath(os.path.join(self._path, "META-INF"))
		self._oebps = os.path.abspath(os.path.join(self._path, "OEBPS"))
		os.mkdir(self._meta)
		os.mkdir(self._oebps)
		with open(os.path.join(self._path, "mimetype"), "wt", encoding = "utf-8") as mimefile:
			mimefile.write("application/epub+zip")
		#Contents pretty much the same always but use lxml anyway
		E = ElementMaker(nsmap = {None: "urn:oasis:names:tc:opendocument:xmlns:container"})
		rootfile_tag = E.rootfile()
		rootfile_tag.set("full-path", "OEBPS/content.opf")
		rootfile_tag.set("media-type", "application/oebps-package+xml")
		topelem = E.container(
			E.rootfiles(
				rootfile_tag
				),
			version="1.0"
			)
		tree = topelem.getroottree()
		tree.write(os.path.join(self._meta, "container.xml"), pretty_print = True,
				   xml_declaration = True, encoding = "utf-8")
	
	def __init__(self, title, author, uid, language="en-US"):
		"""Creates temporary space for epub file, and writes simple files.
		Call write() to create final output.

		Call close() to clear temporary space on the file system.

		Attributes are set on object using same names, e.g. title, author,
		uid and language and can be changed the same way"""
		self.title = title
		self.author = author
		self.uid = uid
		self.language = language
		#This holds everything the user adds in a list of tuples
		#(Filename in OEBPS, media-type, Title or None, id - Text)
		self._files = []
		self._path = os.path.abspath(tempfile.mkdtemp())
		#Content.opf creators
		#OPF duplicate declarations to get exactly the namespacing behaviour we want from lxml
		self._DCMI = ElementMaker(namespace = DCMI)
		self._OPF = ElementMaker(nsmap = {None: OPF, "opf": OPF, "dc": DCMI})
		self._NCX = ElementMaker(nsmap = {None: NCX})
		self._standard_setup()

	def close(self):
		"""Clears filesystem of redundant files, obsoletes object.

		MAKE SURE TO CALL THIS ALWAYS."""
		shutil.rmtree(self._path)

	def _flush(self):
		"""Internal function that writes XML files into directory. Regenerates
		content-dependent data."""
		
		O = self._OPF
		N = self._NCX

		o_ncx = O.item(id = "ncx", href = "toc.ncx")
		o_ncx.set("media-type", "application/x-dtbncx+xml")
		manifest = O.manifest(o_ncx)
		spine = O.spine(toc="ncx")
		navmap = N.navMap()
		#Keep track of content added for ncx play order
		play_order = 1
		
		for filename, media, title, uid in self._files:
			item = O.item(id = uid, href = filename)
			item.set("media-type", media)
			manifest.append(item)
			#No title for content, its a resource.
			#Therefore, not in spine or ncx
			if title is None:
				continue
			spine.append(O.itemref(idref = uid))
			navmap.append(N.navPoint(
				N.navLabel(
					N.text(title),
					),
				N.content(src = filename),
				id = ("nav" + str(play_order)),
				playOrder = str(play_order)
				))
			play_order += 1
		
		#Generate full trees
		opf_topelem = O.package(
			O.metadata(
				*self._dcmi_tags()
				),
			manifest,
			spine,
			version = "2.0"
			)
		opf_topelem.set("unique-identifier", self._uid_id_str)
		opf_tree = opf_topelem.getroottree()

		ncx_topelem = N.ncx(
			N.head(
				N.meta(name = "dtb:uid", content = self.uid),
				N.meta(name = "dtb:depth", content = "1"),
				N.meta(name = "dtb:totalPageCount", content = "0"),
				N.meta(name = "dtb:maxPageNumber", content = "0")
				),
			N.docTitle(
				N.text(self.title)
				),
			navmap,
			version = "2005-1"
			)
		ncx_tree = ncx_topelem.getroottree()
		
		opf_tree.write(os.path.join(self._oebps, "content.opf"), pretty_print = True,
				   xml_declaration = True, encoding = "utf-8")
		#lxml etree.tostring supports doctype decl but write doesn't
		#As we fix the output to utf-8 in code, do encoding roundtrip to force xml decl from lxml
		ncx_text = etree.tostring(ncx_tree, pretty_print = True, xml_declaration = True,
								  encoding = "utf-8",
								  doctype = "<!DOCTYPE ncx PUBLIC '-//NISO//DTD ncx 2005-1//EN' 'http://www.daisy.org/z3986/2005/ncx-2005-1.dtd'>\n").decode('utf-8')
		with open(os.path.join(self._oebps, "toc.ncx"), "wt", encoding = "utf-8") as ncx:
			ncx.write(ncx_text)

	def write(self, file):
		"""Given an absolute filename, file, write as epub file.
		No extension is added, so provide full file and absolute path.

		Can be called as many times as necessary until close() is called.
		"""
		self._flush()
		
		with zipfile.ZipFile(file, mode="w", compression=zipfile.ZIP_DEFLATED) as epub:

			#Write things outside of OEBPS dir
			#mimetype needs to be uncompressed and first
			epub.write(os.path.join(self._path, "mimetype"), arcname = "mimetype",
					   compress_type=zipfile.ZIP_STORED)
			epub.write(os.path.join(self._meta, "container.xml"),
					   arcname = os.path.join("META-INF", "container.xml"))

			#Walk the directory chain, add everything in OEBPS
			top_len = len(self._path)
			for path, dirnames, filenames in os.walk(self._oebps):
				#Make archive directories relative to top, not absolute
				arc_dir = path[top_len:]
				for filen in filenames:
					epub.write(os.path.join(path, filen), arcname = os.path.join(arc_dir, filen))

	def add(self, arcname, media_type, data, content_title = None):
		"""Main method to add contents to epub file.

		arcname is the epub internal name for a file.
		media_type is the MIME type for a file.
		data is a stream object that contains a file to be added.
		content_title is the title of this file. e.g. Chapter.
		- With no title it is treated as a resource not in the reading
		order.

		Will overwrite previous file with same arcname."""

		#Use md5 as ID, might be useful somewhere.
		md5 = hashlib.md5()
		with open(os.path.join(self._oebps, arcname), "wb") as arcfile:
			block = data.read(md5.block_size)
			if isinstance(block, str):
				block = block.encode()
				data_read = lambda : data.read(md5.block_size).encode()
			else:
				data_read = lambda : data.read(md5.block_size)
			while len(block) != 0:
				md5.update(block)
				arcfile.write(block)
				block = data_read()

		#id's need to start with a letter according to epubcheck
		self._files.append((arcname, media_type, content_title, "h" +
							md5.hexdigest()))

	#Simple context manager support
	def __enter__(self):
		"""Return self to use object as context manager."""
		return self

	def __exit__(self, type, val, tb):
		"""Make sure everything is closed and pass exceptions up."""
		self.close()
		return False
