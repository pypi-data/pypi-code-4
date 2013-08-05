#
#  Model.py
#  Erlenmeyer
#
#  Created by Patrick Perini on February 7, 2013.
#  See LICENSE.txt for licensing information.
#

# imports
import sqlalchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import sqlalchemy as flask_sqlalchemy


# constants 
classMethods = [
    'all',
    'get',
]

instanceMethods = [
    '__iter__',
    'update',
    'save',
    'delete'
]

# class accessors
def all(self, **kwargs):
    if not kwargs:
        return self.query.all()
    else:
        return self.query.filter_by(**kwargs)
    
def get(self, identifier):
    return self.query.get(identifier)

# accessors
def __iter__(self):
    for sqlProperty in flask_sqlalchemy.orm.class_mapper(self.__class__).iterate_properties:
        if sqlProperty.key.startswith('_'):
            continue
           
        if type(sqlProperty) == sqlalchemy.orm.RelationshipProperty:
            if not sqlProperty.uselist: # to-one relationship
                relatedObject = getattr(self, sqlProperty.key)
                if not relatedObject:
                    continue
                
                yield (sqlProperty.key, getattr(relatedObject, sqlProperty.mapper.primary_key[0].key))
               
            else: # to-many relationship
                relatedObjects = getattr(self, sqlProperty.key)
                if not relatedObjects:
                    continue
                
                yield (sqlProperty.key, [getattr(relatedObject, sqlProperty.mapper.primary_key[0].key) for relatedObject in relatedObjects])
        else:
            yield (sqlProperty.key, getattr(self, sqlProperty.key))

# mutators
def update(self, properties):
    for key in properties:
        value = properties[key]
        
        sqlProperty = flask_sqlalchemy.orm.class_mapper(self.__class__).get_property(key)
        if type(sqlProperty) == flask_sqlalchemy.orm.RelationshipProperty:
            if not sqlProperty.uselist: # to-one relationship
                if type(value) == list: # stupid multidict list encapsulation
                    value = value[0]
                
                value = sqlProperty.mapper.class_.get(value)
                
            else: # to-many relationship
                value = [sqlProperty.mapper.class_.get(valueElement) for valueElement in value]
        
        elif type(value) == list: # stupid multidict list encapsulation
            value = value[0]
        
        setattr(self, key, value)

def save(self):
    self.__class__.__database__.session.add(self)
    self.__class__.__database__.session.commit()
    
def delete(self):
    self.__class__.__database__.session.delete(self)
    self.__class__.__database__.session.commit()