#
# Copyright (c) 2009, 2013
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
# THE SOFTWARE.
#
from sqlalchemy import \
    Column, \
    DateTime, \
    Integer, \
    ForeignKey, \
    Sequence, \
    String, \
    and_, or_, \
    select, \
    func, \
    Text
from sqlalchemy.orm import column_property
from base import Base, KVC


class Collection(Base, KVC):
    """ An OpenGroupare Collection object """
    __tablename__ = 'collection'
    __entityName__ = 'Collection'
    __internalName__ = 'Collection'
    object_id = Column(
        'collection_id',
        Integer,
        Sequence('key_generator'),
        ForeignKey('collection_assignment.collection_id'),
        ForeignKey('log.object_id'),
        ForeignKey('object_acl.object_id'),
        primary_key=True, )
    version = Column(
        "object_version",
        Integer)
    owner_id = Column(
        "owner_id",
        Integer,
        ForeignKey('person.company_id'),
        nullable=False, )
    kind = Column("kind", String(50), )
    title = Column("title", String(255), )
    project_id = Column(
        "project_id", Integer,
        ForeignKey('project.project_id'),
        nullable=True, )
    auth_token = Column(
        "auth_token",
        String(12), )
    dav_enabled = Column(
        "dav_enabled",
        Integer, )
    comment = Column(
        "comment",
        Text, )

    def __repr__(self):
        return '<Collection objectId={0} ownerId={1} "{2}">'.\
               format(self.object_id, self.owner_id, self.title, )

    def get_display_name(self):
        return self.title

    @classmethod
    def __declare_last__(cls):

        cls.assignment_count = column_property(
            select([func.count(CollectionAssignment.object_id)]).
            where(CollectionAssignment.collection_id == cls.object_id).
            as_scalar()
        )


class CollectionAssignment(Base, KVC):
    __tablename__ = 'collection_assignment'
    __entityName__ = 'CollectionAssignment'
    __internalName__ = 'CollectionAssignment'

    object_id = Column(
        'collection_assignment_id',
        Integer,
        Sequence('key_generator'),
        primary_key=True, )
    collection_id = Column('collection_id', Integer, )
    assigned_id = Column('assigned_id', Integer, )
    sort_key = Column('sort_key', Integer, )
    entity_name = Column('entity_name', String(42), )

    def __cmp__(self, other):
        if hasattr(other, 'object_id'):
            if (other.object_id > self.object_id):
                return -1
            elif (other.object_id < self.object_id):
                return 1
            return 0
        else:
            return 0

    def __repr__(self):
        return '<CollectionAssignment collectionId={0}' \
               ' assignedId={1} sortKey={2}>'.\
               format(self.collection_id,
                      self.assigned_id,
                      self.sort_key, )
