#
#  {{ metadata.fileName }}
#  {{ metadata.projectName }}
#
#  Created by {{ metadata.fileAuthor }} on {{ metadata.pubDate }} via Erlenmeyer.
#  Copyright (c) {{ metadata.pubYear }} {{ metadata.projectOwner }}. All rights reserved.
#

# imports
from {{ metadata.projectName }} import database

class {{ model.className }} (database.Model):

    # class properties
    __database__ = database

    # properties
    {% for attribute in model.attributes -%}
    {% if attribute.name == model.primaryKey -%}
    {{ attribute.name }} = database.Column(database.{{ attribute.type }}, primary_key = True)
    {% else -%}
    {{ attribute.name }} = database.Column(database.{{ attribute.type }})
    {% endif -%}
    {% else %}
    # - no properties...
    {% endfor %}
    
    # - relationships
    {% for relationship in model.relationships -%}
    {% if relationship.isToMany -%}
    {% if relationship.inverseIsToMany and not relationship.hasBeenAccountedFor -%}
    {{ relationship.name }} = database.tableRelationship(
        '{{ model.className }}',
        '{{ relationship.className }}',
        '{{ model.primaryKey }}',
        database.{{ model.primaryKeyType }},
        inverseName = '{{ relationship.inverseName }}'
    )
    
    {% endif -%}
    {% else -%}
    {% if relationship.hasBeenAccountedFor -%}
    _{{ relationship.name }}_{{ model.primaryKey }} = database.Column(database.{{ model.primaryKeyType }})
    {% else -%}
    _{{ relationship.name }}_{{ model.primaryKey }} = database.Column(database.{{ model.primaryKeyType }}, database.ForeignKey("{{ relationship.className|underscore }}.{{ model.primaryKey }}"))
    {% if relationship.name == relationship.inverseName -%}
    {% if relationship.inverseIsToMany -%}
    {{ relationship.name }} = database.relationship("{{ relationship.className }}", primaryjoin = "{{ model.className }}._{{ relationship.name }}_{{ model.primaryKey }} == {{ relationship.className }}.{{ model.primaryKey }}", foreign_keys = "{{ relationship.className }}.{{ model.primaryKey }}", uselist = False)
    {% else -%}
    {{ relationship.name }} = database.relationship("{{ relationship.className }}", primaryjoin = "{{ model.className }}._{{ relationship.name }}_{{ model.primaryKey }} == {{ relationship.className }}.{{ model.primaryKey }}", foreign_keys = "{{ relationship.className }}.{{ model.primaryKey }}", uselist = False)
    {% endif -%}
    {% else -%}
    {% if relationship.inverseIsToMany -%}
    {{ relationship.name }} = database.relationship("{{ relationship.className }}", backref = database.backref("{{ relationship.inverseName }}"))
    {% else -%}
    {{ relationship.name }} = database.relationship("{{ relationship.className }}", backref = database.backref("{{ relationship.inverseName }}"), uselist = False)
    {% endif -%}
    {% endif -%}
    {% endif -%}
    {% endif %}
    {% else %}
    # - - no relationships...
    {% endfor %}