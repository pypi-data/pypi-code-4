#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from StringIO import StringIO
from utility import \
    normalize_string, \
    normalize_datetime, \
    parse_keywords, \
    subindex_properties


def subindex_company(company, context, stream):

    for address in company.addresses.values():
        stream.write(normalize_string(address.city))
        stream.write(normalize_string(address.name1))
        stream.write(normalize_string(address.name2))
        stream.write(normalize_string(address.name3))
        stream.write(normalize_string(address.street))
        stream.write(normalize_string(address.province))
        stream.write(normalize_string(address.country))
        stream.write(normalize_string(address.district))
        stream.write(normalize_string(address.postal_code))

    for telephone in company.telephones.values():
        if telephone.number:
            tmp = telephone.number
            stream.write(normalize_string(tmp))
            stream.write(
                normalize_string(
                    filter(
                        type(tmp).isdigit,
                        tmp
                    )
                )
            )
        if telephone.info:
            stream.write(normalize_string(telephone.info))

    for company_value in company.company_values.values():
        stream.write(normalize_string(company_value.name))
        if company_value.string_value:
            stream.write(normalize_string(company_value.string_value))


def index_enterprise(enterprise, context):
    # TODO: parse associated_categories
    # TODO: associated_company
    # TODO: associated_contacts
    # TODO: include notes related to enterprse

    stream = StringIO()

    keywords = archived = event_date = None

    if enterprise.status == 'archived':
        archived = True
    else:
        archived = False

    event_date = None

    keywords = parse_keywords(enterprise.keywords, delimiter=' ')

    stream.write(normalize_string(str(enterprise.object_id)))
    stream.write(normalize_string(enterprise.keywords))
    stream.write(normalize_string(enterprise.bank_code))
    stream.write(normalize_string(enterprise.bank))
    stream.write(normalize_string(enterprise.file_as))
    stream.write(normalize_string(enterprise.number))
    stream.write(normalize_string(enterprise.number))
    stream.write(normalize_string(enterprise.comment))

    subindex_properties(enterprise, context, stream)

    subindex_company(enterprise, context, stream)

    return keywords, archived, event_date, stream.getvalue()


def index_contact(contact, context):
    # TODO: parse associated_categories
    # TODO: associated_company
    # TODO: associated_contacts
    # TODO: include notes related to contact

    stream = StringIO()

    keywords = archived = event_date = None

    if contact.status == 'archived':
        archived = True
    else:
        archived = False

    event_date = None

    keywords = parse_keywords(contact.keywords, delimiter=' ')

    stream.write(normalize_string(str(contact.object_id)))
    stream.write(normalize_string(contact.keywords))
    stream.write(normalize_string(contact.assistant_name))
    stream.write(normalize_string(contact.birth_name))
    stream.write(normalize_string(contact.birth_place))
    stream.write(normalize_string(contact.boss_name))
    stream.write(normalize_string(contact.citizenship))
    stream.write(normalize_string(contact.degree))
    stream.write(normalize_string(contact.department))
    stream.write(normalize_string(contact.display_name))
    stream.write(normalize_string(contact.family_status))
    stream.write(normalize_string(contact.last_name))
    stream.write(normalize_string(contact.middle_name))
    stream.write(normalize_string(contact.number))
    stream.write(normalize_string(contact.office))
    stream.write(normalize_string(contact.occupation))
    stream.write(normalize_string(contact.partner_name))
    stream.write(normalize_string(contact.file_as))
    stream.write(normalize_string(contact.comment))
    stream.write(normalize_datetime(contact.birth_date))
    stream.write(normalize_datetime(contact.grave_date))

    subindex_properties(contact, context, stream)

    subindex_company(contact, context, stream)

    for enterprise in (
        context.run_command('contact::get-enterprises',
                            object=contact, )
    ):
        stream.write(normalize_string(enterprise.name))
        stream.write(normalize_string(enterprise.bank_code))
        stream.write(normalize_string(enterprise.bank))
        for address in enterprise.addresses.values():
            stream.write(normalize_string(address.city))
            stream.write(normalize_string(address.province))
            stream.write(normalize_string(address.postal_code))
        for telephone in enterprise.telephones.values():
            if telephone.number:
                stream.write(normalize_string(telephone.number))
                stream.write(normalize_string(
                    filter(
                        type(telephone.number).isdigit,
                        telephone.number,
                    )
                ))

    return keywords, archived, event_date, stream.getvalue()
