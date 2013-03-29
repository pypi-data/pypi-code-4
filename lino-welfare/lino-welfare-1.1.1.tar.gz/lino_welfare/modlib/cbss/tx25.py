# -*- coding: UTF-8 -*-
## Copyright 2011-2013 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
Transaction 25
--------------

This implements the "transaction 25", called also 
"Interrogation sur certains types d’informations légales" 
(in `Codes d'interrogations
<http://www.ibz.rrn.fgov.be/fileadmin/user_upload/Registre/fr/instructions/instr_annexe3_liste_interrogations.pdf>`_).

All common information types are being handled. See :class:`RowHandlers` 

See also:

- `Liste des types d'information (pdf)
  <http://www.ibz.rrn.fgov.be/fileadmin/user_upload/Registre/fr/instructions/IT_FR_20111202.pdf>`__

- `Lijst van de informatietypes (pdf)
  <http://www.ibz.rrn.fgov.be/fileadmin/user_upload/Registre/nl/instructies/IT_NL_20111202.pdf>`__


- `DGIP > Registre national > Instructions
  <http://www.ibz.rrn.fgov.be/index.php?id=2485&L=0>`__


"""

import datetime
import traceback
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from lino import mixins
from lino import dd
#~ from lino.utils import Warning
from lino.utils import join_words
from lino.utils import assert_pure
from lino.utils import AttrDict, IncompleteDate

from lino.utils.xmlgen import html as xghtml
E = xghtml.E


try:
    import suds
except ImportError, e:
    pass


from lino_welfare.modlib.cbss.models import NewStyleRequest,SSIN, get_client, \
  CBSSRequestDetail, CBSSRequests, cbss2gender, RequestStates, CBSS_ERROR_MESSAGE
  
def reply_has_result(reply):
    if reply.status.value == "NO_RESULT":
        msg = CBSS_ERROR_MESSAGE % reply.status.code
        keys = ('value','code','description')
        msg += '\n'.join([
            k+' : '+getattr(reply.status,k)
                for k in keys])
        for i in reply.status.information:
            msg += "\n- %s = %s" % (i.fieldName,i.fieldValue)
        raise Warning(msg)
  
  
class RequestLanguages(dd.ChoiceList):
    verbose_name = _("Language")
add = RequestLanguages.add_item
add("nl",_("Dutch"),"nl")
add("fr",_("French"),"fr")
add("de",_("German"),"de")

class RetrieveTIGroupsRequest(NewStyleRequest,SSIN):
    """
    A request to the RetrieveTIGroups service (aka Tx25)
    """
    
    class Meta:
        verbose_name = _("Tx25 Request")
        verbose_name_plural = _('Tx25 Requests')
        
    wsdl_parts = ('cache','wsdl','RetrieveTIGroupsV3.wsdl')
    
    #~ language = babel.LanguageField()
    language = RequestLanguages.field(blank=True,default=RequestLanguages.fr)
    history = models.BooleanField(
        verbose_name=_("History"),default=True,
        help_text = "Whatever this means.")
        
    def get_print_language(self,pm):
        if settings.SITE.getlanguage_info(self.language.value):
        #~ if self.language.value in babel.AVAILABLE_LANGUAGES:
            return self.language.value
        return settings.SITE.DEFAULT_LANGUAGE.django_code
        
    def fill_from_person(self,person):
        self.national_id = person.national_id
        if RequestLanguages.get_by_value(person.language,None):
            self.language = person.language # .value # babel.DEFAULT_LANGUAGE
        
        
    def get_service_reply(self,**kwargs):
        assert_pure(self.response_xml)
        client = get_client(self)
        meth = client.service.retrieveTI
        clientclass = meth.clientclass(kwargs)
        client = clientclass(meth.client, meth.method)
        #~ print 20120613, portSelector[0]
        #~ print '20120613b', dir(client)
        s = self.response_xml.encode('utf-8')
        return client.succeeded(client.method.binding.input,s)
        
    
    def execute_newstyle(self,client,infoCustomer,simulate_response):
        si = client.factory.create('ns0:SearchInformationType')
        si.ssin = self.get_ssin()
        if self.language:
            si.language = self.language.value
        #~ if self.history:
            #~ si.history = 'true'
        si.history = self.history
        #~ if validate:
            #~ self.validate_newstyle(srvreq)
        if simulate_response is None:
            self.check_environment(si)
            try:
                reply = client.service.retrieveTI(infoCustomer,None,si)
            except suds.WebFault,e:
                """
                Example of a SOAP fault:
          <soapenv:Fault>
             <faultcode>soapenv:Server</faultcode>
             <faultstring>An error occurred while servicing your request.</faultstring>
             <detail>
                <v1:retrieveTIGroupsFault>
                   <informationCustomer xmlns:ns0="http://kszbcss.fgov.be/intf/RetrieveTIGroupsService/v1" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/">
                      <ticket>2</ticket>
                      <timestampSent>2012-05-23T10:19:27.636628+01:00</timestampSent>
                      <customerIdentification>
                         <cbeNumber>0212344876</cbeNumber>
                      </customerIdentification>
                   </informationCustomer>
                   <informationCBSS>
                      <ticketCBSS>f4b9cabe-e457-4f6b-bfcc-00fe258a9b7f</ticketCBSS>
                      <timestampReceive>2012-05-23T08:19:09.029Z</timestampReceive>
                      <timestampReply>2012-05-23T08:19:09.325Z</timestampReply>
                   </informationCBSS>
                   <error>
                      <severity>FATAL</severity>
                      <reasonCode>MSG00003</reasonCode>
                      <diagnostic>Unexpected internal error occurred</diagnostic>
                      <authorCode>http://www.bcss.fgov.be/en/international/home/index.html</authorCode>
                   </error>
                </v1:retrieveTIGroupsFault>
             </detail>
          </soapenv:Fault>
                """
                
                msg = CBSS_ERROR_MESSAGE % e.fault.faultstring
                msg += unicode(e.document)
                self.status = RequestStates.failed
                raise Warning(msg)
            self.response_xml = reply.decode('utf-8') # 20130201
        else:
            self.response_xml = simulate_response
            
        #~ self.response_xml = unicode(reply)
        reply = self.get_service_reply()
        self.ticket = reply.informationCBSS.ticketCBSS
        self.status = RequestStates.warnings
        
        reply_has_result(reply)
            
        self.status = RequestStates.ok
        #~ self.response_xml = str(res)
        #~ self.response_xml = "20120522 %s %s" % (res.__class__,res)
        #~ print 20120523, res.informationCustomer
        #~ print self.response_xml
        return reply
        
          
    def Result(self,ar):
        return ar.spawn(RetrieveTIGroupsResult,master_instance=self)
        
        
  
class RetrieveTIGroupsRequestDetail(CBSSRequestDetail):
  
    parameters = dd.Panel("national_id language history",label=_("Parameters"))
    
    result = "cbss.RetrieveTIGroupsResult"
    
    #~ def setup_handle(self,lh):
        #~ CBSSRequestDetail.setup_handle(self,lh)
        
#~ class RetrieveTIGroupsRequestInsert(dd.FormLayout):
    #~ window_size = (40,'auto')
    #~ main = """
    #~ person
    #~ national_id language 
    #~ history
    #~ """

class RetrieveTIGroupsRequests(CBSSRequests):
    #~ debug_permissions = True
    model = RetrieveTIGroupsRequest
    detail_layout = RetrieveTIGroupsRequestDetail()
    column_names = 'id user person national_id language history status ticket sent environment'
    #~ insert_layout = RetrieveTIGroupsRequestInsert()
    insert_layout = dd.FormLayout("""
    person
    national_id language 
    history
    """,window_size = (40,'auto'))
    #~ insert_layout = RetrieveTIGroupsRequestInsert(window_size=(400,'auto'))
    required_user_groups = ['cbss']
        
    #~ @dd.virtualfield(dd.HtmlBox())
    #~ def result(self,row,ar):
        #~ return row.response_xml
        
class RetrieveTIGroupsRequestsByPerson(RetrieveTIGroupsRequests):
    master_key = 'person'
    
class MyRetrieveTIGroupsRequests(RetrieveTIGroupsRequests,mixins.ByUser):
    pass
    





def rn2date(rd):
    return IncompleteDate(int(rd.Century+rd.Year),int(rd.Month),int(rd.Day))
    
def deldate(n):
    if hasattr(n,'DelDate'):
        return [' (' + unicode(_('until ')) + dd.dtos(rn2date(n.DelDate)) + ')']
    #~ return [' (' + unicode(_('until today')) + ')']
    return []
    #~ return []
    
    
#~ def simpleattr(n,name):
    #~ v = getattr(n,name,None)
    #~ if v:
        #~ return [ ', '+name+' ' + unicode(v)]
    #~ return []
    
def simpletype(v):
    return Info(xghtml.E.b(unicode(v)))
def boldstring(v):
    return Info(xghtml.E.b(unicode(v)))
    
def validate_element(c):
    if c is None:
        raise Exception("Invalid element %r" % c)
        
class Info(object):
    def __init__(self,*chunks):
        for c in chunks: validate_element(c)
        self.chunks = list(chunks)
    def addfrom(self,node,name,prefix=None,fmt=boldstring,suffix=''):
        v = getattr(node,name,None)
        if not v: return self
        if prefix is None:
            prefix = '%s ' % name
        else:
            prefix = force_unicode(prefix)
        if len(self.chunks):
            if not prefix.startswith(' '):
                prefix = ', ' + prefix
        if prefix and prefix[-1] not in ' :':
            prefix += ': '
        self.chunks += [prefix] + fmt(v).chunks
        if suffix:
            self.chunks.append(force_unicode(suffix))
        return self
    def add_deldate(self,n):
        self.chunks += deldate(n)
    def add_codelabel(self,n):
        self.chunks += code_label(n).chunks
        #~ if hasattr(n,'Label'):
            #~ self.addfrom(n,'Label')
            #~ self.addfrom(n,'Code','(',simpletype,')')
        #~ else:
            #~ self.addfrom(n,'Code','[',boldstring,']')
        return self
    
def code_label(n):
    if hasattr(n,'Label') and n.Label:
        return Info(E.b(n.Label),' (',n.Code,')')
    return Info(E.b(n.Code))

def datarow(group,node,since,info):
    if group and node.__class__.__name__.startswith('IT'):
        itnum = node.__class__.__name__[2:]
    else:
        itnum = ''
    if hasattr(node,'Type'):
        group += " " + node.Type
    #~ if hasattr(node,'Status'):
        #~ group += " " + unicode(node.Status)
    if hasattr(node,'Structure'):
        group += " " + node.Structure
    return AttrDict(group=group,
        type=itnum,since=rn2date(since),info=E.p(*info.chunks))
    
#~ CodeLabel = code_label
#~ def CodeLabel(n):
    #~ info = Info()
    #~ return info
    
def NameType(n):
    info = Info()
    s = ' '.join([ln.Label for ln in n.LastName])
    info.chunks.append(E.b(s))
    if hasattr(n,'FirstName'):
        info.chunks.append(', ')
        s = ' '.join([fn.Label for fn in n.FirstName])
        info.chunks.append(s)
    return info
    
    

#~ def addinfo(node,name,prefix=None,fmt=simpletype,suffix=''):
    #~ v = getattr(node,name,None)
    #~ if not v: return []
    #~ if prefix is None:
        #~ prefix = ', %s ' % name
    #~ info = [force_unicode(prefix)] + fmt(v)
    #~ if suffix:
        #~ info.append(force_unicode(suffix))
    #~ return info
    
def DateType(n):
    return Info(dd.dtos(rn2date(n)))
    
def ForfeitureDateType(n):
    info = Info(dd.dtos(rn2date(n)))
    info.addfrom(n,'Graphic',' (',simpletype,')')
    return info
    
def ExpiryDateType(n):
    info = Info(dd.dtos(rn2date(n)))
    info.addfrom(n,'Graphic',' (',simpletype,')')
    return info
    
def TribunalType(n):
    return code_label(n)
def PlaceType(n):
    return code_label(n)
def GraphicPlaceType(n):
    info = CountryType(n.Country)
    info.addfrom(n,'Graphic','')
    #~ if hasattr(n,'Graphic'):
        #~ info.append(', graphic:'+n.Graphic)
    return info
def ForeignJudgementType(n):
    return GraphicPlaceType(n.Place)
def BelgianJudgementType(n):
    info = Info()
    info.addfrom(n,'Tribunal',None,TribunalType)
    info.addfrom(n,'Date',None,DateType)
    info.addfrom(n,'Place',None,PlaceType)
    #~ info += TribunalType(n.Tribunal)
    #~ info += DateType(n.Date)
    #~ info += PlaceType(n.Place)
    return info
def CountryType(n):
    return code_label(n)
def LieuType(n):
    info = Info()
    if hasattr(n,'Place1'):
        #~ info += code_label(n.Place1)
        info.addfrom(n,'Place1',None,code_label)
    elif hasattr(n,'Place2'):
        info.addfrom(n,'Place2',None,GraphicPlaceType)
    else:
        place = n.Place3
        #~ info += GraphicPlaceType(place)
        info.addfrom(place,'BelgianJudgement','',BelgianJudgementType)
        info.addfrom(place,'ForeignJudgement','',ForeignJudgementType)
        #~ if hasattr(place,'BelgianJudgement'):
            #~ info += BelgianJudgementType(place.BelgianJudgement)
        #~ else:
            #~ info += ForeignJudgementType(place.ForeignJudgement)
    return info

def DeliveryType(n):
    return PlaceType(n.Place)
    
def DiplomaticPostType(n):
    return code_label(n)
def TerritoryType(n):
    return code_label(n)
def ProvinceType(n):
    return code_label(n)
    
def IssuerType(n):
    # prefixes can be empty since this is a xs:choice
    info = Info().addfrom(n,'Place','',PlaceType)
    info.addfrom(n,'Province','',ProvinceType,' (%s)' % unicode(_("Province")))
    info.addfrom(n,'PosteDiplomatique','',DiplomaticPostType,' (%s)' % unicode(_("Diplomatic post")))
    return info

def ResidenceType(n):
    return code_label(n)
    
def NationalNumberType(n):
    info = Info().addfrom(n,'NationalNumber','')
    return info # [n.NationalNumber]
    
def PartnerType(n):
    info = Info().addfrom(n,'NationalNumber','',NationalNumberType)
    #~ info.addfrom(n,'Name','',NameType)
    info.addfrom(n,'Name',' ',NameType)
    return info
    
def NotaryType(n):
    info = Info().addfrom(n,'NameNotary')
    info.addfrom(n,'Place',' in ',PlaceType)
    info.addfrom(n,'Country',', ',CountryType)
    return info
    
def NotificationType(n):
    info = Info().addfrom(n,'NotificationDate',None,DateType)
    info.addfrom(n,'Place',' in ',PlaceType)
    return info
    
def ReasonType(n):
    return code_label(n)
    
def CessationType(n):
    return code_label(n)
    
def DeclarationType(n):
    return code_label(n)
    
def Residence(n):
    info = Info().addfrom(n,'Residence','',ResidenceType)
    info.addfrom(n,'Fusion',_("Fusion"))
    info.addfrom(n,'Language',_("Language"))
    info.add_deldate(n)
    return info
    
    
def IT003(n): # AscertainedLegalMainAddresses : Détermination de résidence
    #~ raise Exception(str(n))
    def InvestigationResultType(n): 
        return code_label(n)
    info = Info().addfrom(n,'InvestigationResult','',InvestigationResultType)
    info.addfrom(n,'Graphic1','')
    info.addfrom(n,'Graphic2','')
    info.add_deldate(n)
    return info
  
def IT005(n): # AddressChangeIntention
    #~ raise Exception(str(n))
    info = Info().addfrom(n,'OriginPlace',_('Move from '),PlaceType)
    info.addfrom(n,'DestinationPlace',_('Move to '),PlaceType)
    info.add_deldate(n)
    return info
  
def IT006(n):
    info = Info()
    info.addfrom(n,'Country','',CountryType)
    info.addfrom(n,'Graphic',' ')
    info.add_deldate(n)
    return info

def IT011(n): # Pseudonymes
    info = Info()
    info.addfrom(n,'Name','',NameType)
    info.add_deldate(n)
    return info
  
def IT013(n):
    info = Info()
    info.addfrom(n,'ModificationType','',ModificationTypeType)
    info.addfrom(n,'Graphic','')
    info.add_deldate(n)
    return info

def IT018(n):
    info = Info()
    info.addfrom(n,'Address','',AddressType)
    info.add_deldate(n)
    return info

def IT024(n): 
    info = Info()
    info.add_deldate(n)
    return info

def IT208(n):
    info = Info()
    #~ info.addfrom(n,'Date','',DateType)
    info.addfrom(n,'PseudoNationalNumber','')
    info.add_deldate(n)
    return info


def IT073(n):
    info = Info()
    info.addfrom(n,'Category','',CategoryType)
    info.addfrom(n,'CertificateNumber',_("no."))
    info.add_deldate(n)
    return info

def IT074(n):
    info = Info()
    info.addfrom(n,'SerialNumber')
    info.addfrom(n,'IdentificationNumber')
    info.add_deldate(n)
    return info


def FiliationType(n):
    return code_label(n)

def ParentType(n):
    info = Info()
    info.addfrom(n,'Name','',NameType)
    info.addfrom(n,'NationalNumber',' (',NationalNumberType,')')
    return info
    
def StreetType(n):
    # we don't print the code of streets
    info = Info()
    info.addfrom(n,'Label','')
    #~ info.addfrom(n,'NationalNumber',' (',NationalNumberType,')')
    return info
    #~ return code_label(n)

def IT020(n):
    def AddressType020(n):
        info = Info()
        info.addfrom(n,'ZipCode','')
        info.addfrom(n,'Street','',StreetType)
        info.addfrom(n,'HouseNumber',_('no. '))
        info.addfrom(n,'Box',' ')
        return info
    info = Info()
    info.addfrom(n,"Address",'',AddressType020)
    return info
  
def IT110(n):
    #~ info = code_label(n.FiliationType)
    #~ info.addfrom(n.Parent1,'Name','',NameType)
    #~ info.addfrom(n.Parent1,'NationalNumber',' (',NationalNumberType,')')
    #~ info.chunks.append(_('and '))
    #~ info.addfrom(n.Parent2,'Name','',NameType)
    #~ info.addfrom(n.Parent2,'NationalNumber',' (',NationalNumberType,')')
    info = Info()
    info.addfrom(n,'FiliationType','',FiliationType)
    #~ info.chunks.append()
    info.addfrom(n,'Parent1',_('of '),ParentType)
    info.addfrom(n,'Parent2',_('and '),ParentType)
    info.addfrom(n,'ActNumber',_("Act no. "))
    info.addfrom(n,'Place',_("in "),PlaceType)
    info.addfrom(n,'Graphic'," ")
    info.add_deldate(n)
    return info
    
def IT140(n):
    info = Info().addfrom(n,'Name',' ',NameType)
    info.addfrom(n,'NationalNumber',' (',NationalNumberType,')')
    #~ info += _(' as ')
    info.addfrom(n,'FamilyRole',_('as '),code_label)
    info.addfrom(n,'Housing',None,HousingType)
    info.add_deldate(n)
    return info
    
def IT141(n):
    info = Info()
    info.addfrom(n,'Housing',None,HousingType)
    info.addfrom(n,'FamilyRole','',code_label)
    info.addfrom(n,'Name',_('in family headed by '),NameType)
    info.addfrom(n,'NationalNumber',' (',NationalNumberType,')')
    info.add_deldate(n)
    return info
        
def NationalityType(n):
    return code_label(n)
    
def IT213(n): # Alias
    info = Info()
    info.addfrom(n,'Name','',NameType)
    info.addfrom(n,'Nationality',None,NationalityType)
    info.addfrom(n,'BirthDate',_(' born '),DateType)
    info.addfrom(n,'BirthPlace',_(' in '))
    info.add_deldate(n)
    return info
  
  
def TypeOfLicenseType(n):
    return code_label(n)
    
def TypeOfLicenseType194(n):
    return code_label(n)
    
def DeliveryType194(n):
    info = Info().addfrom(n,'Place',_('in '),PlaceType)
    info.addfrom(n,'Label','')
    info.addfrom(n,'Code',' (',simpletype,')')
    #~ info.add_codelabel(n)
    #~ info += code_label(n)
    return info
    
def CategoryType(n):
    return code_label(n)
    
def GearBoxType(n):
    return code_label(n)
    
def MedicalType(n):
    return code_label(n)
    
def LicenseCategoriesType(n):
    info = Info()
    #~ raise Exception(str(n))
    #~ for cat in n.Category:
        #~ info.addfrom(cat,'Category',' ',CategoryType)
    info.chunks.append('/'.join([cat.Label for cat in n.Category]))
    #~ info += code_label(n)
    return info
    
def ForfeitureReasonType(n):
    return code_label(n)
    
def IT191(n):
    #~ info = code_label(n.TypeOfLicense)
    info = Info().addfrom(n,'TypeOfLicense','',TypeOfLicenseType)
    info.addfrom(n,'LicenseNumber',_('no. '))
    info.addfrom(n,'Place',_('delivered in '),PlaceType)
    info.addfrom(n,'DeliveryCountry',' (',CountryType,')')
    info.addfrom(n,'ForfeitureReason',None,ForfeitureReasonType)
    info.addfrom(n,'ForfeitureDate',None,ForfeitureDateType)
    #~ info.append()
    #~ info.append(E.b(n.LicenseNumber))
    #~ info.append(', categories ' 
      #~ + ' '.join([cat.Label for cat in n.Categories.Category]))
    #~ info.append(_(' delivered in '))
    #~ info += code_label(n.Delivery.Place)
    info.add_deldate(n)
    return info
    
def IT194(n):
    info = Info().addfrom(n,'TypeOfLicense','',TypeOfLicenseType194)
    info.addfrom(n,'Categories',_('categories '),LicenseCategoriesType)
    info.addfrom(n,'LicenseNumber',_('no. '))
    info.addfrom(n,'Delivery',_('delivered '),DeliveryType194)
    info.addfrom(n,'GearBox',None,GearBoxType)
    info.addfrom(n,'Medical',None,MedicalType)
    info.addfrom(n,'ExpiryDate',_('expires '),ExpiryDateType)
    info.add_deldate(n)
    return info
    
def IT198(n):
    info = Info().addfrom(n,'PermitNumber',_('no. '))
    info.addfrom(n,'Categories',_('categories '),LicenseCategoriesType)
    info.addfrom(n,'LicenseNumber',_('no. '))
    info.addfrom(n,'Delivery',_('delivered '),DeliveryType194)
    info.addfrom(n,'GearBox',None,GearBoxType)
    info.addfrom(n,'Medical',None,MedicalType)
    info.addfrom(n,'ExpiryDate',_('expires '),ExpiryDateType)
    info.add_deldate(n)
    return info
    



def TypeOfPassportType(n):
    return code_label(n)
    
def PassportIdentType(n):
    info = Info()
    info.addfrom(n,'PassportType',_('type '),TypeOfPassportType)
    info.addfrom(n,'PassportNumber',_('no. '))
    return info
    
def IT199(n):
    info = Info()
    #~ info.chunks.append('Number ')
    #~ info.chunks.append(E.b(n.PassportIdent.PassportNumber))
    #~ info.append(', status ')
    info.addfrom(n,'Status',_("status"),code_label)
    info.addfrom(n,'PassportIdent','',PassportIdentType)
    info.addfrom(n,'Issuer',_('issued by '),IssuerType)
    info.addfrom(n,'RenewalNumber',_('renewal no. '),boldstring)
    info.addfrom(n,'SerialNumber',_('serial no. '),boldstring)
    info.addfrom(n,'SecondNumber',_('second no. '),boldstring)
    info.addfrom(n,'ReplacementOf',_('replacement of '),boldstring)
    info.addfrom(n,'AdditionTo',_('addition to '),boldstring)
    info.addfrom(n,'ProductionDate',_('produced '),DateType)
    info.addfrom(n,'ExpiryDate',_('expires '),DateType)
    #~ info.append(', type ')
    #~ info += code_label(n.PassportIdent.PassportType)
    #~ info.append(', expires ')
    #~ info.append(E.b(dd.dtos(rn2date(n.ExpiryDate))))
    #~ info.append(', delivered by ')
    #~ info += code_label(n.Issuer.PosteDiplomatique)
    #~ info.append(_(' renewal no. '))
    #~ info.append(E.b(n.RenewalNumber))
    info.add_deldate(n)
    return info

def HousingType(n):
    return code_label(n)
    
def ModificationTypeType(n):
    return code_label(n)
    
def AddressType(n):
    info = Info()
    #~ pd = n.Address.Address
    info.addfrom(n,'Country','',CountryType)
    #~ info.append(', ')
    info.addfrom(n,'Graphic1','')
    info.addfrom(n,'Graphic2','')
    info.addfrom(n,'Graphic3','')
    #~ info.append(E.b(pd.Graphic1))
    #~ info.append(', ')
    #~ info.append(E.b(pd.Graphic2))
    #~ info.append(', ')
    #~ info.append(E.b(pd.Graphic3))
    #~ info.addfrom(pd,'Graphic3')
    return info
    

def CertificateType(n):
    return code_label(n)
    




def IT200(n):
    info = Info().addfrom(n,'PublicSecurityNumber',_('no. '))
    info.add_deldate(n)
    return info
    
def IT202(n):
    info = Info()
    info.addfrom(n,'Graphic1','')
    info.addfrom(n,'Graphic2','')
    info.addfrom(n,'Limosa','',LimosaType)
    info.add_deldate(n)
    return info
def LimosaType(n):
    info = Info()
    info.addfrom(n,'Reason1','',LimosaReasonType)
    info.addfrom(n,'Reason2','',LimosaReasonType)
    info.addfrom(n,'NationalNumber',_('SSIN '),NationalNumberType)
    return info
def LimosaReasonType(n):
    return code_label(n)
    
def IT205(n):
    info = code_label(n)
    info.add_deldate(n)
    return info
    
def OrganizationType(n): return code_label(n)
def GeneralInfoType(n):
    info = code_label(n)
    info.addfrom(n,'Organization',_("Organization"),OrganizationType)
    return info
    
def OrigineType(n): 
    return Info().add_codelabel(n)
def AppealType(n):  return code_label(n)
def StatusAppealType(n):  return code_label(n)
def ProcedureType(n):
    info = Info()
    info.addfrom(n,'Origine',None,OrigineType)
    info.addfrom(n,'Reference')
    info.addfrom(n,'Appeal',None,AppealType)
    info.addfrom(n,'OpenClose',None,StatusAppealType)
    info.addfrom(n,'NationalNumber',_('SSIN '),NationalNumberType)
    return info
    
def DecisionCancelledType(n):
    info = Info()
    info.addfrom(n,'Date',None,DateType)
    info.addfrom(n,'Reference')
    return info
def DelayLeaveGrantedType(n):
    info = Info()
    info.addfrom(n,'Date',None,DateType)
    return info
def StrikingOutType(n):
    info = Info()
    info.addfrom(n,'Reference')
    info.addfrom(n,'OpenClose',None,OpenCloseType)
    info.addfrom(n,'Status',None,StrikingStatusType)
    return info
def StrikingStatusType(n):  return code_label(n)
def TerritoryLeftType(n):  return code_label(n)
def OpenCloseType(n):  return code_label(n)

def ProtectionType(n):
    info = code_label(n)
    info.addfrom(n,'Reference')
    info.addfrom(n,'Term')
    return info
    
def AdviceFromCGVSType(n):
    info = code_label(n)
    info.addfrom(n,'Reference')
    return info
    
def ApplicationFiledType(n):
    info = code_label(n)
    info.addfrom(n,'Place',_("in "),PlaceType)
    return info
    
def DecisionType206(n):
    info = code_label(n)
    info.addfrom(n,'Reference',_("Reference"))
    info.addfrom(n,'OpenClose',_("Open/Close"),OpenCloseType)
    info.addfrom(n,'Comments')
    info.addfrom(n,'Term')
    return info
    
def NotificationByDVZType(n):
    info = Info()
    info.addfrom(n,'Place',_("in "),PlaceType)
    info.addfrom(n,'Reference')
    return info
    
def NotificationByOrgType(n):
    info = Info()
    info.addfrom(n,'Reference')
    return info
    
def AppealLodgedType(n):
    info = Info()
    info.addfrom(n,'Reference')
    return info
    
def IT206(n):
    def Status(n):
        info = Info()
        info.addfrom(n,'Status')
        return info
        
    info = Info()
    info.addfrom(n,'GeneralInfo','',GeneralInfoType)
    info.addfrom(n,'Procedure',_("Procedure"),ProcedureType)
    info.addfrom(n,'StrikingOut',None,StrikingOutType)
    info.addfrom(n,'DecisionCancelled',_("Decision cancelled"),DecisionCancelledType)
    info.addfrom(n,'Protection',_("Protection"),ProtectionType)
    info.addfrom(n,'DelayLeaveGranted',None,DelayLeaveGrantedType)
    info.addfrom(n,'Escape',_("Escape"),Status)
    info.addfrom(n,'UnrestrictedStay',None,Status)
    info.addfrom(n,'ApplicationRenounced',_("Application renounced"),Status)
    info.addfrom(n,'TerritoryLeft',_("Territory left"),TerritoryLeftType)
    info.addfrom(n,'AdviceFromCGVS',None,AdviceFromCGVSType)
    info.addfrom(n,'Decision',_("Decision"),DecisionType206)
    info.addfrom(n,'ApplicationFiled',_("Application filed"),ApplicationFiledType)
    info.addfrom(n,'NotificationByDVZ',None,NotificationByDVZType)
    info.addfrom(n,'NotificationByOrg',None,NotificationByOrgType)
    info.addfrom(n,'AppealLodged',None,AppealLodgedType)
    info.add_deldate(n)
    return info
    


def InitiativeType(n):
    return code_label(n)
    
def SocialWelfareType(n):
    info = Info()
    info.addfrom(n,'Place',_("in "),PlaceType)
    info.addfrom(n,'Initiative',None,InitiativeType)
    info.add_deldate(n)
    return info
    
def RefugeeCentreType(n):
    return code_label(n)
    
def IT207(n):
    info = Info()
    info.addfrom(n,'SocialWelfare',_("Social Welfare Centre"),SocialWelfareType)
    info.addfrom(n,'RefugeeCentre',_("Refugee Centre"),RefugeeCentreType)
    info.add_deldate(n)
    return info
    
def RegistrationRegisterType(n):
    return code_label(n)
def IT210(n):
    info = Info()
    info.addfrom(n,'RegistrationRegister',_("Registration register"),RegistrationRegisterType)
    info.add_deldate(n)
    return info
    



def IdentificationType(n):
    return code_label(n)
def IT211(n):
    info = Info()
    info.addfrom(n,'TypeOfDocument','',IdentificationType)
    info.add_deldate(n)
    return info
    




def ChoosenResidenceType(n):
    return code_label(n)
def IT212(n):
    info = Info().addfrom(n,'Residence',None,ChoosenResidenceType)
    info.addfrom(n,'Graphic','')
    info.add_deldate(n)
    return info
    
def IT251(n):
    info = Info()
    info.add_deldate(n)
    return info
    
    

class RowHandlers:
    """
    The result of a Tx25 consist of data rows, each of which has a given type.
    Consult the source code of this class to see how it works.
    
    TODO: present here a complete list of the supported TIs (generated from source code).
    
    """
    
    @staticmethod
    def IT000(n,name):
        group = _("National Number")
        #~ group = name
        n = n.NationalNumber
        info = Info(
          E.b(n.NationalNumber),
          ' ('+unicode(cbss2gender(n.Sex))+')')
        yield datarow(group,n,n.Date,info)
        
    @staticmethod
    def IT019(n,name):
        group = _("Address Change Declaration") 
        #~ print 20120829, n
        info = Info()
        
        def AddressType(n):
            info = Info()
            info.addfrom(n,'Graphic','')
            return info
        
        info.addfrom(n,'Address','',AddressType)
        info.add_deldate(n)
        yield datarow(group,n,n.Date,info)


    @staticmethod
    def FileOwner(fo,name):
        group = _("Residences")
        for n in fo.Residences:
            info = Residence(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def AscertainedLegalMainAddresses(fo,name):
        group = _("Ascertained Legal Main Addresses") # Détermination de résidence
        #~ raise Exception(str(fo))
        #~ raise Exception(repr([n for n in fo]))
        for n in fo.AscertainedLegalMainAddress:
            info = IT003(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def Pseudonyms(fo,name):
        group = _("Pseudonyms") # Pseudonymes
        for n in fo.Pseudonym:
            info = IT011(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def Aliases(fo,name):
        group = _("Aliases")
        for n in fo.Alias:
            info = IT213(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def AddressChangeIntention(fo,name):
        group = _("Address Change Intention") # Intention de changer l'adresse
        for n in fo.Address:
            info = IT005(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def AddressReferences(fo,name):
        group = _("Address References") # Adresse de référence
        for n in fo.AddressReference:
            info = IT024(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            

      
    @staticmethod
    def Names(node,name):
        group = _("Names")
        #~ group = name
        for n in node.Name:
            info = Info().addfrom(n,'Name','',NameType)
            yield datarow(group,n,n.Date,info)
            group = ''
        

    @staticmethod
    def LegalMainAddresses(node,name):
        group = _("Legal Main Addresses")
        for n in node.LegalMainAddress:
            yield datarow(group,n,n.Date,IT020(n))
            group = ''
            #~ info = Info()
            #~ info.chunks.append(E.b(n.Address.ZipCode))
            #~ info.chunks.append(', ')
            #~ info.chunks.append(n.Address.Street.Label)
            #~ info.chunks.append(' ')
            #~ info.chunks.append(n.Address.HouseNumber)
            #~ yield datarow(group,n,n.Date,info)
            #~ group = ''
            

    @staticmethod
    def ResidenceAbroad(node,name):
        def ResidenceAbroadAddressType(n):
            info = Info('Address')
            info.addfrom(n,'PosteDiplomatique',None,DiplomaticPostType)
            info.addfrom(n,'Territory',' ',TerritoryType)
            info.addfrom(n,'Address',' ',AddressType)
            return info
        group = _("Residence Abroad")
        for n in node.ResidenceAbroad:
            info = Info()
            info.addfrom(n,'Address','',ResidenceAbroadAddressType)
            
            #~ info += code_label(n.Address.PosteDiplomatique)
            #~ info.append(', ')
            #~ info += code_label(n.Address.Territory)
            #~ info.append(', ')
            info.add_deldate(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def Nationalities(node,name):
        group = _("Nationalities")
        for n in node.Nationality:
            info = code_label(n.Nationality)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def Occupations(node,name):
        group = _("Occupations")
        for n in node.Occupation:
            info = code_label(n.Occupation)
            info.addfrom(n,'SocialCategory',' (SC ',code_label,')')
            #~ info.append(' (SC ')
            #~ info += code_label(n.SocialCategory)
            #~ info.append(')')
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def IT100(n,name):
        group = _("Birth Place")
        #~ n = res.BirthPlace
        #~ info = code_label(n.Place1)
        #~ info.append(' (' + n.ActNumber + ')')
        info = Info()
        info.addfrom(n,'Place1',_('in '),PlaceType)
        info.addfrom(n,'Place2',_('in '),GraphicPlaceType)
        info.addfrom(n,'ActNumber',_("Act no. "))
        info.addfrom(n,'SuppletoryRegister')
        yield datarow(group,n,n.Date,info)
        
        
    @staticmethod
    def IT101(n,name):
        group = _("Declared Birth Date") # Date de naissance déclarée
        info = Info()
        info.addfrom(n,'DeclaredBirthDate','',DateType)
        info.addfrom(n,'Certificate','',CertificateType)
        info.add_deldate(n)
        yield datarow(group,n,n.Date,info)
        
        
    @staticmethod
    def Filiations(node,name):
        group = _("Filiations")
        for n in node.Filiation:
            info = IT110(n)
            yield datarow(group,n,n.Date,info)
            group = ''
          
        
    @staticmethod
    def CivilStates(node,name):
        group = _("Civil States") # IT120
        for n in node.CivilState:
            info = code_label(n.CivilState)
            if hasattr(n,'Spouse'):
                #~ info.append(' with ')
                #~ info += name2info(n.Spouse.Name)
                info.addfrom(n.Spouse,'Name',_('with '),NameType)
                info.chunks.append(' (')
                info.chunks.append(n.Spouse.NationalNumber.NationalNumber)
                info.chunks.append(')')
            info.addfrom(n,'Lieu',_('in '),LieuType)
            #~ info += LieuType(n.Lieu)
            info.addfrom(n,'ActNumber',_("Act no. "))
            #~ info.addfrom(n,'ActNumber')
            info.addfrom(n,'SuppletoryRegister')
            info.add_deldate(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def FamilyMembers(node,name):
        group = _("Family Members")
        for n in node.FamilyMember:
            info = IT140(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
    @staticmethod
    def HeadOfFamily(node,name):
        group = _("Head Of Family")
        for n in node.HeadOfFamily:
            info = IT141(n)
            yield datarow(group,n,n.Date,info)
            group = ''
          
    @staticmethod
    def DrivingLicensesOldModel(node,name):
        group = _("Driving Licenses Old Model")
        for n in node.DrivingLicense:
            info = IT194(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def DrivingLicenses(node,name):
        group = _("Driving Licenses")
        for n in node.DrivingLicense:
            info = IT191(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def WorkPermits(node,name):
        group = _("Work Permits") # Permis de travail
        for n in node.WorkPermit:
            info = IT198(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def PublicSecurityNumbers(node,name):
        group = _("Public Security Numbers") # No de securite publique
        for n in node.PublicSecurityNumber:
            info = IT200(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def SpecialInfos(node,name):
        group = _("Special Infos") 
        for n in node.SpecialInfo:
            info = IT202(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def RefugeeTypes(node,name):
        group = _("Refugee Types") # Type de Personne dans le registre d'attente
        for n in node.RefugeeType:
            info = IT205(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def StatusOfRefugee(node,name):
        group = _("Status of refugee") # Statut de refugie
        for n in node.StatusOfRefugee:
            info = IT206(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def IdentityCards(node,name):
        group = _("Identity Cards")
        for n in node.IdentityCard:
            info = code_label(n.TypeOfCard)
            info.chunks.append(' ')
            info.chunks.append(_('no. '))
            info.chunks.append(E.b(n.CardNumber))
            info.addfrom(n,'ExpiryDate',_('expires '),DateType)
            #~ info.chunks.append(E.b(dd.dtos(rn2date(n.ExpiryDate))))
            info.addfrom(n,'Delivery',_('delivered in '),DeliveryType)
            #~ info.chunks.append(', delivered in ')
            #~ info += code_label(n.Delivery.Place)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def LegalCohabitations(node,name):
        def CessationType(n):
            info = Info()
            info.addfrom(n,'Reason',_("Reason"),ReasonType)
            info.addfrom(n,'Place',_('in '),PlaceType)
            info.addfrom(n,'Notification',_('in '),NotificationType)
            return info
      
        def DeclarationType(n):
            info = Info()
            info.addfrom(n,'RegistrationDate','',DateType)
            info.addfrom(n,'Partner',_('with '),PartnerType)
            info.addfrom(n,'Place',_('in '),PlaceType)
            info.addfrom(n,'Notary',_('in '),NotaryType)
            return info
    
        group = _("Legal cohabitations")
        for n in node.LegalCohabitation:
            info = Info()
            info.addfrom(n,'Declaration',_("Declaration"),DeclarationType)
            info.addfrom(n,'Cessation',_("Cessation"),CessationType)
            info.add_deldate(n)
            yield datarow(group,n,n.Date,info)
            group = ''
            
      
    @staticmethod
    def Passports(node,name):
        group = _("Passports")
        for n in node.Passport:
            info = IT199(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def OrganizationsInCharge(node,name):
        group = _("Organizations in charge")
        for n in node.OrganizationInCharge:
            info = IT207(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def RegistrationRegisters(node,name):
        group = _("Registration registers")
        for n in node.RegistrationRegister:
            info = IT210(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def ChoosenResidences(node,name):
        group = _("Choosen residences")
        for n in node.ChoosenResidence:
            info = IT212(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def OrganDonations(node,name):
        group = _("Organ Donations")
        for n in node.OrganDonation:
            info = Info().addfrom(n,'Declaration','',DeclarationType)
            info.addfrom(n,'Place',_('in '),PlaceType)
            info.add_deldate(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def ResidenceUpdateDates(node,name):
        group = _("Residence Update Dates") # Date mise à jour de la résidence principale
        for n in node.ResidenceUpdateDate:
            info = IT251(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def DocumentTypes(node,name):
        group = _("Document Types") # Type de document pour déterminer identité
        for n in node.DocumentType:
            info = IT211(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def NameModifications(node,name):
        group = _("Name Modifications") # Type de document pour déterminer identité
        for n in node.NameModification:
            info = IT013(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def CountriesOfOrigin(node,name):
        group = _("Countries Of Origin") # Pays d'origine
        for n in node.CountryOfOrigin:
            info = IT006(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def AddressDeclarationAbroad(node,name):
        group = _("Address Declaration Abroad") 
        for n in node.Address:
            info = IT018(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def PseudoNationalNumbers(node,name):
        group = _("Pseudo National Numbers") # Pseudo-numéro national
        for n in node.PseudoNationalNumber:
            info = IT208(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def RetirementCertificates(node,name):
        group = _("Retirement Certificates") # Certificats de pension
        for n in node.RetirementCertificate:
            info = IT073(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def SpecialRetirementCertificates(node,name):
        group = _("Special Retirement Certificates") # Certificats de pension spéciale
        for n in node.SpecialRetirementCertificate:
            info = IT074(n)
            yield datarow(group,n,n.Date,info)
            group = ''
        
    @staticmethod
    def IT253(node,name):
        group = _("Creation Date")
        n = node # res.CreationDate
        info = Info()
        yield datarow(group,n,n.Date,info)
        
    @staticmethod
    def IT254(node,name):
        group = _("Last Update")
        n = node # res.LastUpdateDate
        info = Info()
        yield datarow(group,n,n.Date,info)
        

class RetrieveTIGroupsResult(dd.VirtualTable):
    """
    Displays the response of an :class:`RetrieveTIGroupsRequest`
    as a table.
    """
    master = RetrieveTIGroupsRequest
    master_key = None
    label = _("Results")
    column_names = 'group:18 type:5 since:14 info:50'
    
    @dd.displayfield(_("Group"))
    def group(self,obj,ar):
        return obj.group
            
    @dd.displayfield(_("TI"))
    def type(self,obj,ar):
        return obj.type
            
    @dd.virtualfield(models.DateField(_("Since")))
    def since(self,obj,ar):
        return obj.since
            
    @dd.displayfield(_("Info"))
    def info(self,obj,ar):
        return obj.info
            
    @classmethod
    def get_data_rows(self,ar):
        rti = ar.master_instance
        if rti is None: 
            #~ print "20120606 ipr is None"
            return
        #~ if not ipr.status in (RequestStates.ok,RequestStates.fictive):
        #~ if not rti.status in (RequestStates.ok,RequestStates.warnings):
            #~ return
        reply = rti.get_service_reply()
        if reply is None:
            return
        reply_has_result(reply)
        
        res = reply.rrn_it_implicit
        
        for name, node in res:
            #~ print name, node.__class__
            m = getattr(RowHandlers,node.__class__.__name__,None)
            if m is None:
                raise Exception("No handler for %s (%s)" 
                    % (name, node.__class__.__name__))
            else:
                for row in m(node,name): yield row
            
        
        
        
            
__all__ = [
  'RetrieveTIGroupsRequest', 
  'RetrieveTIGroupsRequests',
  'RetrieveTIGroupsRequestsByPerson',
  'MyRetrieveTIGroupsRequests',
  'RetrieveTIGroupsResult',
]
