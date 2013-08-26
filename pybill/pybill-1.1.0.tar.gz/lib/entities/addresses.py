# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.addresses`` module contains the definition of the entities
related to the address description.

These entities contain data information related to person or company addresses,
and are used by other classes.

.. autoclass:: Address
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: PersonAddress
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: OrganisationAddress
   :members:
   :undoc-members:
   :show-inheritance: 

"""
__docformat__ = "restructuredtext en"


class Address:
    """
    Abstract class containing common parts for ``PersonAddress`` and
    ``OrganisationAddress`` classes.

    .. attribute:: streets

       Attribute containing the several `street` lines of the address (because
       the `street` definition can be complex and need several lines). Can be
       empty.

       type: list of :class:`unicode`

    .. attribute:: post_box

       Attribute defining the post box described in the address. Can be empty.
       
       type: :class:`unicode`

    .. attribute:: post_code

       Attribute defining the post code of the address. Can be empty but is
       often filled.

       type: :class:`unicode`

    .. attribute:: city

       Attribute defining the city described in the address. Can be empty but is
       often filled.

       type: :class:`unicode`

    .. attribute:: state

        Attribute containing the state described in the address. In some
        countries, the addresses don't contain a specification of state. Can be
        empty.

        type: :class:`unicode`

    .. attribute:: country

        Attribute defining the country of the address. Is often not filled when
        the sender and the receiver are in the same country. Can be empty.

        type: :class:`unicode`

    .. attribute:: phone

       Attribute containing the phone number. Only one phone number is
       allowed. Can be empty.

       type: :class:`unicode`

    .. attribute:: fax

       Attribute containing the fax number. Only one fax number is allowed. Can
       be empty.
        
       type: :class:`unicode`

    .. attribute:: web

        Attribute containing the web site address. Only one web site address is
        allowed. Can be empty.

        type: :class:`unicode`

    .. attribute:: email

       Attribute containing the email address. Only one email address is
       allowed. Can be empty.

       type: :class:`unicode`

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes an object.

        This object is empty and will be filled later by the XML readers.
        """
        if self.__class__ is Address:
            raise NotImplementedError("Abstract class cann't be instanciated.")
        self.streets = []
        self.post_box = u""
        self.post_code = u""
        self.city = u""
        self.state = u""
        self.country = u""
        self.phone = u""
        self.fax = u""
        self.web = u""
        self.email = u""

    def get_postal_address_lines(self):
        """
        Gives the list of the various lines of the postal address.

        Some pieces of information are displayed on the same line (e.g. post
        code and city). Some pieces of information (e.g. phone, email, etc.) are
        not in the list because they don't concern the postal address. Doesn't
        return empty lines.

        :returns: The list of the various lines of the postal address. Each line
                  is an Unicode string.
        :rtype: list of :class:`unicode`
        """
        lines = []

        for street in self.streets:
            if u" ".join(street.split()) != u'':
                lines.append(u" ".join(street.split()))

        if u" ".join(self.post_box.split()) != u'':
            lines.append(u" ".join(self.post_box.split()))

        city_line = u"%s %s %s" % (self.post_code, self.city, self.state)
        if u" ".join(city_line.split()) != u'':
            lines.append(u" ".join(city_line.split()))

        if u" ".join(self.country.split()) != u'':
            lines.append(u" ".join(self.country.split()))

        return lines


class PersonAddress(Address):
    """
    Entity class describing the address of a person (used for sender and
    receiver of the accounting documents).

    This class specializes the base class ``Address`` and contains only the
    attributes and methods to deal with the person name (other fields of the
    address are managed by the base class).

    .. attribute:: honorific

       Attribute containing the honorific used to designate the person (e.g.
       u"Mr", u"Ms", u"Dr"). Can be empty.

       type: :class:`unicode`

    .. attribute:: firstname

       Attribute containing the first name of the person. Can be empty.

       type: :class:`unicode`

    .. attribute:: other_name

       Attribute defining the other name. Other name contains other pieces of
       data concerning the name that are not a honorific, a first name, a
       surname or a lineage. These pieces of data are often written between the
       first name and the name. Can be empty.  Sometimes ``other_name`` contains
       all the name and the other fields are empty (data is not splitted accross
       all the fields).

       type: :class:`unicode`

    .. attribute:: surname

       Attribute defining the surname of the person. Can be empty.

       type: :class:`unicode`

    .. attribute:: lineage

       Attribute defining the lineage of the person (postfixes the name). E.g.
       u"Sr", u"Jr", u"3rd". Can be empty.

       type: :class:`unicode`

    .. attribute:: organisation

        Attribute containing the organisation (company, society, etc.) where the
        person works. This organisation is described with an
        ``OrganisationAddress`` object.
                        
        type: :class:`~pybill.lib.entities.addresses.OrganisationAddress`

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes an empty object.

        This method calls the ``__init__`` method of the base class
        (``Address``).
        """
        Address.__init__(self)
        self.honorific = u""
        self.firstname = u""
        self.other_name = u""
        self.surname = u""
        self.lineage = u""
        self.organisation = None # OrganisationAddress

    def get_person_name(self):
        """
        Returns the person name in one string (single line).

        This string is composed with the various fields concerning the name:
        ``honorific``, ``firstname``, ``other_name``, ``surname``, ``lineage``.
        
        :returns: Single line containing the name of the person.
        :rtype: :class:`unicode`
        """
        name = "%s %s %s %s %s" % (self.honorific, self.firstname,
                                   self.other_name, self.surname, self.lineage)
        return " ".join(name.split())


class OrganisationAddress(Address):
    """
    Entity class describing the address of an organisation (used in PersonAdress
    to contain data about the company of the sender/receiver).

    This class specializes the base class ``Address`` and contains only the
    attributes and methods to deal with the organisation name and the person
    role in this organisation (other fields of the address are managed by the
    base class).

    .. attribute:: name

       Attribute defining the name of the organisation. Can be empty.

       type: :class:`unicode`

    .. attribute:: divisions

       Attribute containing the list of the various divisions that the person
       working for this organisation is affiliated to. This attribute is used
       when the organisation address is embedded in a person address.  Can be
       empty.

       type: list of :class:`unicode`

    .. attribute:: job_titles

       Attribute containing a list of the various job titles that the person
       working for this organisation has got. This attribute is used when the
       organisation address is embedded in a person address. Can be empty.

       type: list of :class:`unicode`

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes an empty object.

        This method calls the ``__init__`` method of the base class
        (``Address``).
        """
        Address.__init__(self)
        self.name = u""
        self.divisions = []
        self.job_titles = []
