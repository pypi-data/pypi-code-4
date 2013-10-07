from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField.Column import Column
from Products.PloneGlossary.interfaces import IPloneGlossaryDefinition
from zope.component import adapts
from zope.interface import implements


class MyDataGridField1(ExtensionField, DataGridField):
    """A datagrid field """


class MyDataGridField2(ExtensionField, DataGridField):
    """A datagrid field """


class GlossaryDefinitionExtender(object):
    adapts(IPloneGlossaryDefinition)
    implements(ISchemaExtender)

    fields = [
        MyDataGridField1("term_translations",
            columns=("language", "term"),
            widget=DataGridWidget(
                columns={
                    'language': Column("Language"),
                    'term': Column("Glossary Term"),
                },
            ),
        ),

        MyDataGridField2("definition_translations",
            columns=("language", "definition"),
            widget=DataGridWidget(
                columns={
                    'language': Column("Language"),
                    'definition': Column("Glossary definition"),
                },
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
