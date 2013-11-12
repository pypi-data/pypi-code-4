from lxml import etree

from plone.supermodel.parser import ISchemaMetadataHandler
from plone.supermodel.utils import ns
from zope.interface import implements

NAME_FROM_PERSON = u'seantis.people.name_from_person'
PERSON_COLUMNS = u'seantis.people.person_column'
PERSON_ORDER = u'seantis.people.order'
PERSON_SELECTABLE = u'seantis.people.selectable'
PERSON_DETAILS = u'seantis.people.details'
PERSON_COLUMN_TITLE = u'senatis.people.column_title'

# Supermodel namespace and prefix
PEOPLE_NAMESPACE = 'http://namespaces.plone.org/supermodel/people'
PEOPLE_PREFIX = 'people'

missing = object()


def get_title_fields(schema):
    """ Get the fields used by INameFromPerson. """
    return schema.queryTaggedValue(NAME_FROM_PERSON, [])


def set_title_fields(schema, fields):
    """ Sets the fields used by INameFromPerson. """
    schema.setTaggedValue(NAME_FROM_PERSON, sorted(
        list(set(fields)), key=fields.index  # unique values, preserving order
    ))


def get_order(schema):
    """ Gets the fields by which the person list is ordered. """
    return schema.queryTaggedValue(PERSON_ORDER, [])


def set_order(schema, order):
    """ Sets the fields by which the person list is ordered. """
    schema.setTaggedValue(PERSON_ORDER, order)


def get_detail_fields(schema):
    """ Gets the fields shown in the detail view by position. E.g.

    {
        'left': ['firstname', 'lastname'],
        'right': ['image']
    }

    """
    return schema.queryTaggedValue(PERSON_DETAILS, {})


def set_detail_fields(schema, fields):
    """ Sets the fields shown in the detail view by position. """
    schema.setTaggedValue(PERSON_DETAILS, fields)


def get_columns(schema):
    return schema.queryTaggedValue(PERSON_COLUMNS, [])


def set_columns(schema, columns):
    for column in columns:
        assert not isinstance(column, basestring), """
            A list of lists is expected, not a list of strings.
        """
    schema.setTaggedValue(PERSON_COLUMNS, columns)


def get_selectable_fields(schema):
    return schema.queryTaggedValue(PERSON_SELECTABLE, [])


def set_selectable_fields(schema, fields):
    schema.setTaggedValue(PERSON_SELECTABLE, list(set(fields)))


def get_custom_column_titles(schema):
    return schema.queryTaggedValue(
        PERSON_COLUMN_TITLE, [None for col in get_columns(schema)]
    )


def set_custom_column_titles(schema, titles):
    schema.setTaggedValue(PERSON_COLUMN_TITLE, titles)


class NodeHandler(object):

    namespace = PEOPLE_NAMESPACE
    prefix = PEOPLE_PREFIX

    def __init__(self, tagname):
        self.tagname = tagname
        etree.register_namespace(self.prefix, self.namespace)

    def xpath(self, node, expression):
        return node.xpath(expression, namespaces={'people': self.namespace})

    def prefixed(self, name):
        return ns(name, self.namespace)

    def nodes(self, node, name):
        return node.findall('./{}'.format(self.prefixed(name)))

    def tags(self, node):
        return self.nodes(node, self.tagname)

    def items(self, node):
        return self.text(self.nodes(node, 'item'))

    def text(self, nodes):
        return [n.text.strip() for n in nodes]


class ItemListHandler(NodeHandler):

    def __init__(self, tagname, getter, setter):
        super(ItemListHandler, self).__init__(tagname)
        self.getter = getter
        self.setter = setter

    def parse(self, schema_node, schema):
        expression = 'people:{}/people:item'.format(self.tagname)
        self.setter(schema, self.text(self.xpath(schema_node, expression)))

    def write(self, schema_node, schema):
        values = self.getter(schema)

        if not values:
            return

        element = etree.Element(self.prefixed(self.tagname))
        for value in values:
            item = etree.Element(self.prefixed('item'))
            item.text = value

            element.append(item)

        schema_node.append(element)


class DetailsHandler(NodeHandler):

    def parse(self, schema_node, schema):
        tags = self.tags(schema_node)

        if not tags:
            return

        detail_fields = {}

        for tag in tags:
            detail_fields[tag.get('position') or 'left'] = self.items(tag)

        set_detail_fields(schema, detail_fields)

    def write(self, schema_node, schema):
        detail_fields = get_detail_fields(schema)

        if not detail_fields:
            return

        for position, fields in detail_fields.items():
            element = etree.Element(self.prefixed(self.tagname))
            element.set('position', position)

            for field in fields:
                item = etree.Element(self.prefixed('item'))
                item.text = field

                element.append(item)

            schema_node.append(element)


class ColumnsHandler(NodeHandler):

    def parse(self, schema_node, schema):
        tags = self.tags(schema_node)

        if not tags:
            return

        columns, selectable_fields, titles = [], [], []

        for tag in tags:
            for column in self.nodes(tag, 'column'):
                column_items = self.items(column)

                if len(column_items) == 1 and column.get('selectable'):
                    selectable_fields.append(column_items[0])

                titles.append(column.get('title'))
                columns.append(column_items)

        set_columns(schema, columns)
        set_selectable_fields(schema, selectable_fields)
        set_custom_column_titles(schema, titles)

    def write(self, schema_node, schema):
        columns = get_columns(schema)
        selectable_fields = get_selectable_fields(schema)
        titles = get_custom_column_titles(schema)

        if not columns:
            return

        columns_el = etree.Element(self.prefixed(self.tagname))

        for ix, column in enumerate(columns):
            column_el = etree.Element(self.prefixed('column'))

            if len(column) == 1 and column[0] in selectable_fields:
                column_el.set('selectable', 'true')

            if titles[ix]:
                column_el.set('title', titles[ix])

            for field in column:
                item_el = etree.Element(self.prefixed('item'))
                item_el.text = field
                column_el.append(item_el)

            columns_el.append(column_el)

        schema_node.append(columns_el)


class PeopleSchemaMetaHandler(object):

    implements(ISchemaMetadataHandler)

    namespace = PEOPLE_NAMESPACE
    prefix = PEOPLE_PREFIX

    handlers = [
        ItemListHandler('title', get_title_fields, set_title_fields),
        ItemListHandler('order', get_order, set_order),
        DetailsHandler('details'),
        ColumnsHandler('columns')
    ]

    def read(self, schema_node, schema):
        for handler in self.handlers:
            handler.parse(schema_node, schema)

    def write(self, schema_node, schema):
        for handler in self.handlers:
            handler.write(schema_node, schema)
