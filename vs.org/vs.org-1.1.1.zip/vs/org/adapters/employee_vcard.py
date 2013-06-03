################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import implements
from ..interfaces import IVCardData
import pycountry

class EmployeeVCard(object):
    """ 
    Adapt an employee to vcard data 
    """

    implements(IVCardData)

    def __init__(self, context):
        self.context = context

    def getVCardData(self):

        emp = self.context

        result = dict() 
        result['id'] = emp.getId()
        result['source'] = emp.absolute_url()
#        result['degree'] = emp.getDegree()
#        result['degree_after'] = emp.getDegreeAfter()
        result['degree'] = ''
        result['firstname'] = emp.getFirstname()
        result['lastname'] = emp.getLastname()
        result['position'] = emp.getPosition()
        result['institution'] = emp.getInstitution().Title()
        result['email'] = emp.getEmail()
        result['url'] = emp.getUrl()
        result['notes'] = ''

        for num_type in ('phone', 'fax', 'mobile'):
            numbers = emp.getNumbersByType(num_type)
            if numbers:
                result[num_type] = numbers[0]
            else:
                result[num_type] = None

        # full vcardname
        lst = [emp.getSalutation(),
#               emp.getDegree(),
               emp.getFirstname(),
               emp.getLastname(),
               emp.getPosition(),
               emp.getDegreeAfter(),
               ]
        lst = [item.strip() for item in lst if item.strip()]
        result['vcardname'] = ' '.join(lst)

        # image
        thumb_data = None
        image_field = emp.getField('image')
        if image_field:
            try:
                thumb_data = str(image_field.getScale(emp, 'thumb').data)
            except AttributeError:
                thumb_data = None
        result['image'] = thumb_data

        # addresses
        addresses = list()
        for ref in emp.getBRefs(relationship='isEmployee'):

            # iterate over Department and Institution addresses
            # (department addresses are more specific than institution addresses)
            orga_hierarchy  = [ref.getInstitution()]
            if ref.portal_type == 'Department':
                orga_hierarchy.insert(0, ref.getDepartment())

            for o in orga_hierarchy:
                for address in o.getAddresses():

                    # expand country and province codes first
                    country_a2 = o.getCountry()
                    try:
                        country_name = pycountry.countries.get(alpha2=country_a2).name
                    except KeyError:
                        country_name = ''

                    province_code = o.getProvince()
                    try:
                        province_name = pycountry.subdivisions.get(code=province_code).name
                    except KeyError:
                        province_name = ''

                    addresses.append(dict(zipcode=address['zipCode'],
                                          city=address['city'],
                                          street=address['street'],
                                          pobox=address['poBox'],
                                          country=country_name,
                                          province=province_name,
                                        ))
        result['addresses'] = addresses

        return result
