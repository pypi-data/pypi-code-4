# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,              #
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez             #
# Christian Martel                                                              #
#                                                                               #
# This program is free software; you can redistribute it and/or                 #
# modify it under the terms of the GNU General Public License                   #
# as published by the Free Software Foundation; either version 2                #
# of the License, or (at your option) any later version.                        #
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software                   #
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#                                                                               #
#################################################################################

__doc__ = """ Zope Exist OAI Templates """


#######  general  Templates #############
namespaceTemplate = 'declare namespace %s;\n'

queryTemplate_T = """xquery version "%(xquery_version)s";
%(nsdeclaration)s
let $col := collection('%(mdlocation)s')
%(letSequence)s
return transform:transform(%(resTemplate)s, %(xslFilter)s , ())"""


queryTemplate_F = """xquery version "%(xquery_version)s";
%(nsdeclaration)s
%(function)s
let $col := collection('%(mdlocation)s')
%(letSequence)s
%(setControl)s
%(dateControl)s
let $md3 := local:prepareBlock($md2[position()>=%(start)s and position()<=%(stop)s])
return
    <records len="{count($md2)}">{$md3}</records>"""

queryTemplate_GetRecord = """xquery version "%(xquery_version)s";
%(nsdeclaration)s
%(function)s
let $col := collection('%(mdlocation)s')
%(letSequence)s
return $md1"""

rangeDateFunction_template = """
declare function local:isDateTime($thisnode as node()*) {
    if (string-length(string($thisnode)) = 10)
        then xs:dateTime(fn:concat(string($thisnode), 'T00:00:00Z'))
    else if (empty($thisnode))
        then xs:dateTime('1990-01-01T00:00:00Z')
    else
        xs:dateTime($thisnode)
};

declare function local:untilTest($nodes as node()*, $until as xs:dateTime) as node()*{
    for $md in $nodes
        where local:isDateTime(%(publicationDate)s) <= $until
            return $md
};

declare function local:fromTest($nodes as node()*, $from as xs:dateTime) as node()*{
    for $md in $nodes
        where local:isDateTime(%(publicationDate)s) >= $from
            return $md
};
"""

fromFunctionCall_template = """let $md2 := local:fromTest($md11, xs:dateTime('%(fromDate)s'))"""
untilFunctionCall_template = """let $md2 := local:untilTest($md11, xs:dateTime('%(untilDate)s'))"""
rangeFunctionCall_template = """let $md12 := local:fromTest($md11, xs:dateTime('%(fromDate)s'))
let $md2 := local:untilTest($md12, xs:dateTime('%(untilDate)s'))"""
emptyFunctionCall_template = """let $md2 := $md11"""


setControlTemplate = """let $md11 := $md1[%(setControl)s] """
setEmptyControlTemplate = """let $md11 := $md1"""

#######  get_earliestDatestamp  Templates #############
## return the earliestDatestamp of the database ressources

gds_template = """xquery version "%(xquery_version)s";
declare namespace util="http://exist-db.org/xquery/util";
declare namespace xmldb="http://exist-db.org/xquery/xmldb";

declare function local:sortMe($a as item()*) {
    for $md in $a order by xmldb:last-modified(util:collection-name($md), util:document-name($md))
        return xmldb:last-modified(util:collection-name($md), util:document-name($md))
};

let $col := collection('%(mdlocation)s')
let $mds := $col//*
return local:sortMe($mds)[1]"""

#######  get_ListMetadataFormats  Templates #############

#lmf_predicateTemplate = """let $md%(indice)s := name($col//%(rootNode)s[%(idPath)s &= '%(identifier)s'])\n"""
lmf_predicateTemplate = """let $md%(indice)s := name(subsequence($col//%(rootNode)s[contains(%(idPath)s, '%(identifier)s')], 1, 1))\n"""

lmf_resTemplate = "<rootNode>{$md%s}</rootNode>"

xslExtractPrefix = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format"><xsl:output method="html"/>
<xsl:template match="metadataPrefix">
      <xsl:for-each select="rootNode"><xsl:value-of select="." />,</xsl:for-each>
      </xsl:template>
    </xsl:stylesheet>"""

#######  get_GetRecord Templates #############
gr_predicateTemplate = """let $md%(indice)s := local:prepareBlock($col//%(rootNode)s[contains(%(idPath)s, '%(identifier)s')])\n"""
#gr_predicateTemplate = """let $md%(indice)s := local:prepareBlock($col//%(rootNode)s[%(idPath)s &= '%(identifier)s'])\n"""

gr_resTemplate = "{$md%s}"

gr_function = """declare namespace xmldb="http://exist-db.org/xquery/xmldb";
declare namespace util="http://exist-db.org/xquery/util";

declare function local:prepareBlock($nodes as node()*) as node()*{
    for $md in $nodes
        let $IDHeader := <identifier>%(identifier)s</identifier>
        let $date := %(publicationDate)s
        let $dateHeader := <datestamp>{$date}</datestamp>
        let $body := <%(oai_rootNode)s xmlns:%(oai_ns)s %(md_ns)s>{$md/*}</%(oai_rootNode)s>
        return
            <record>
                <header>{$IDHeader}{$dateHeader}</header>
                <metadata>{$body}</metadata>
            </record>
};"""


###### Regular expression Template #########
import re
re_extractRecord = re.compile("(<header>(?:.*?)</header>)\s*(<metadata>(?:.*?)</metadata>)", re.MULTILINE | re.DOTALL)
re_extractRecords = re.compile("(<record>(?:.*?)</record>)", re.MULTILINE | re.DOTALL)
re_extractIdentifiers = re.compile("(<header>(?:.*?)</header>)", re.MULTILINE | re.DOTALL)
re_extractLenOfRecords = re.compile('<records len="(.*?)">', re.MULTILINE | re.DOTALL)
re_earliestDatestamp = re.compile("""<exist:value type="xs:dateTime">(.*?)</exist:value>""", re.MULTILINE | re.DOTALL)

###### About Informations when sending records ########
# you can put informations here as describe in the OAI Protocol
# see http://www.openarchives.org/OAI/openarchivesprotocol.html
about_infos = ""



#######  get_ListRecords Templates #############
lr_predicateTemplate = """let $md%(indice)s := local:prepareBlock($col//%(rootNode)s)\n"""


## Standard
lr_function = """declare namespace xmldb="http://exist-db.org/xquery/xmldb";
declare namespace util="http://exist-db.org/xquery/util";

""" + rangeDateFunction_template + """

declare function local:prepareBlock($nodes as node()*) as node()*{
    for $md in $nodes
        let $IDHeader := <identifier>{
            if (not($md/%(idPath)s) or $md/%(idPath)s='')
                then util:document-name($md)
                else $md/%(idPath)s/text()
            }</identifier>
        let $date := %(publicationDate)s
        let $dateHeader := <datestamp>{$date}</datestamp>
        let $body := <%(oai_rootNode)s xmlns:%(oai_ns)s %(md_ns)s>{$md/*}</%(oai_rootNode)s>
        return
            <record>
                <header>{$IDHeader}{$dateHeader}</header>
                <metadata>{$body}</metadata>
                <about>%(about)s</about>
            </record>
};"""


## With XSL Filter
lrT_function = """declare namespace xmldb="http://exist-db.org/xquery/xmldb";
declare namespace util="http://exist-db.org/xquery/util";
(:declare namespace datetime="http://exist-db.org/xquery/datetime";:)

""" + rangeDateFunction_template + """

declare function local:prepareBlock($nodes as node()*) as node()*{
    for $md in $nodes
        let $IDHeader := <identifier>{
            if (not($md/%(idPath)s) or $md/%(idPath)s='')
                then util:document-name($md)
                else $md/%(idPath)s/text()
            }</identifier>
        let $date := %(publicationDate)s
        let $dateHeader := <datestamp>{$date}</datestamp>
        let $md1 := transform:transform($md, '%(xslFilter)s' , <parameters><param name="meta_uri" value="{document-uri($md)}"/></parameters>)
        let $body := <%(oai_rootNode)s xmlns:%(oai_ns)s %(md_ns)s>{$md1/*}</%(oai_rootNode)s>
        return
            <record>
                <header>{$IDHeader}{$dateHeader}</header>
                <metadata>{$body}</metadata>
                <about>%(about)s</about>
            </record>
};"""


#######  get_ListRecordsIdentifiers Templates #############
li_predicateTemplate = """let $md%(indice)s := local:prepareBlock($col//%(rootNode)s)\n"""


li_function = """declare namespace xmldb="http://exist-db.org/xquery/xmldb";
declare namespace util="http://exist-db.org/xquery/util";

""" + rangeDateFunction_template + """

declare function local:prepareBlock($nodes as node()*) as node()*{
    for $md in $nodes
        let $IDHeader := <identifier>{
            if (not($md/%(idPath)s) or $md/%(idPath)s='')
                then util:document-name($md)
                else $md/%(idPath)s/text()
            }</identifier>
        let $date := %(publicationDate)s
        let $dateHeader := <datestamp>{$date}</datestamp>
        let $body := <%(oai_rootNode)s xmlns:%(oai_ns)s %(md_ns)s>{$md/*}</%(oai_rootNode)s>
        return
                <header>{$IDHeader}{$dateHeader}</header>
};"""


#######  get_ListSets Templates #############
setTemplate = """<set>
    <setSpec>%(setSpec)s</setSpec>
    <setName>%(setName)s</setName>
    <setDescription>
        %(setDescription)s
    </setDescription>
</set>"""


