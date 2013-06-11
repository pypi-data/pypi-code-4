""" Copyright (c) 2013 Josh Matthias <jmatthias4570@gmail.com> """

import collections.abc
from collections import defaultdict
import inspect
import sqlalchemy
import sqlalchemy.ext.mutable

from side_effect_containers import (
    SideEffectSet,
    SideEffectList,
    )



def setup(global_dict, session, sqlalchemy_base):
    global DBSession
    global SQLAlchemyBase
    
    DBSession = session
    SQLAlchemyBase = sqlalchemy_base
    
    MultiClassRelationshipSetupManager.setup(global_dict)
    NodeLikeSetupManager.setup()



# -------------------------- Exception classes ---------------------------

class Error(Exception):
    """ Base class for errors. """

class NodeLoopError(Error):
    """ A node-like object occurs more than once in a node tree.
        
        In other words, a node-like object is a descendant of itself. """

class RelatedObjectTypeError(TypeError, Error):
    """ An object of an invalid type was provided as a parent or child
        value. """

class ParentNotFoundError(Error):
    """ An entry for a parent object could not be found based upon the
        '..._id' and '..._tablename' column values of a child object using a
        'MultiClassParent' descriptor. """

class MultipleChildrenError(Error):
    """ More than one child correlates to a single parent using a
        'MonoClassChild' descriptor. """

class RequiredChildError(Error):
    """ A related 'child' was not found for a 'MonoClassChild' using the
        'required' argument. """



# --------------------------- Useful things ----------------------------

def get_all(obj_class, obj_ids):
    query = DBSession().query(obj_class)
    return [query.get(item) for item in obj_ids]

def delete_all(items):
    """ Calls item.delete() for each item in list. """
    # Make a copy for destructive iteration!
    items = list(items)
    for item in items:
        item.delete()

def delete_or_expunge(obj):
    s = DBSession()
    if obj in s.new:
        s.expunge(obj)
        return
    
    try:
        s.delete(obj)
    except sqlalchemy.exc.InvalidRequestError:
        pass

def delete_or_expunge_all(items):
    for item in items: delete_or_expunge(item)

def make_defaultdict_of_set():
    return defaultdict(set)

class MutationTrackerList(sqlalchemy.ext.mutable.Mutable, SideEffectList):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, MutationTrackerList):
            return value
        
        return MutationTrackerList(value)
    
    def _replace_sequence(self, old, new, i):
        self.changed()

def ListColumnType(column_type):
    return MutationTrackerList.as_mutable(postgresql.ARRAY(column_type))



# ------------------------- Custom session class -------------------------

class CustomSession(sqlalchemy.orm.Session):
    """\
        A custom subclass of sqlalchemy.orm.Session.
        
        Always calls .flush() immediately before .commit().
        
        This class substitutes a modified .commit() method for the original
        Session.commit() method. This method always calls .flush() before
        calling .commit(). The purpose is to force the 'after_flush' event to
        occur BEFORE the 'before_commit' event.
        
        This arrangement makes it possible to perform checks on session data
        right before it is committed to the database.
        
        The original commit method would call .flush() from within, IF .flush()
        had not been called since the most recent change to the session data.
        The result was that calling .commit() would give this sequence of events
        if .flush() *had not* been called:
            
            before_commit
            before_flush
            after_flush
            after_commit
        
        ... and this sequence of events if .flush() *had* been called:
            
            before_commit
            after_commit
        
        Note that the original .commit() method would skip the call to .flush()
        entirely if flush had already been called.
        
        In the original arrangement, there was no reliable way to call a routine
        AFTER the session had been flushed, but BEFORE the session had
        committed. This was a big problem, because default values for object
        Column() properties are only assigned AFTER the object has been flushed.
        
        Calling .flush() immediately before .commit() gives this sequence of
        events:
            
            before_flush
            after_flush
            before_commit
            after_commit
        
        This modified arrangement does not functionally change the behavior of
        the Session class; and it is now possible to reliably perform data
        check after flush and before commit.
        """
    
    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        
        self.checker = SessionPreCommitChecker(self)
    
    def commit(self):
        """\
            Modified commit procedure.
            
            Call .flush() before the original .commit() method, always.
            
            'expire_all' must be called before 'commit'; this is for the various
            checking routines which occur before committing. Without calling
            'expire_all', changes that are to-be-committed but that are not
            reflected in the current instances will not be detected. Calling
            'expire_all' probably has a negative effect on performance. """
        self.flush()
        self.expire_all()
        super().commit()
    
    def delete_all(self, instances):
        for item in instances: self.delete(item)

class SessionPreCommitChecker(object):
    """ Performs various checking routines before the session is committed. """
    def __init__(self, session):
        self.session = session
        
        self.ids = {
            key: collection_maker()
            for key, collection_maker in self.id_collections.items()
            }
    
    def pre_commit_check(
        self,
        class_obj,
        ids_set,
        checking_routine,
        *pargs
        ):
        """ Check objects with 'checking_routine.
            
            It is necessary to store the id values (and then query for the
            instances before checking) instead of storing the instances
            themselves, because the instances might be
            no-longer-session-persistent by the time 'pre_commit_check()' is
            called; this would raise an InvalidRequestError. """
        if not ids_set:
            return
        
        q = self.session.query(class_obj)
        objs_to_check = [x for x in [q.get(item) for item in ids_set] if x]
        
        checking_pargs = pargs
        for obj in objs_to_check:
            result = checking_routine(obj, *checking_pargs)
            if result:
                checking_pargs = result
    
    def get_all(self, target_classinfo):
        all_objs = list(set(
            list(self.session.new) +
            list(self.session.dirty) +
            list(self.session.deleted)
            ))
        
        return [obj for obj in all_objs if isinstance(obj, target_classinfo)]
    
    id_collections = {}



# ----------------- MultiClassRelationship descriptors -----------------

class MultiClassRelationship(object):
    """ A relationship that can accommodate multiple classes on one end.
        
        Subclasses must define these methods:
            - expire_related
            - _setup
        
        """
    
    @property
    def parent_obj_attr_name(self):
        return '_{}_parent_obj'.format(self.parent_key)
    
    @property
    def childthing_obj_attr_name(self):
        return '_{}_childthing_obj'.format(self.childthing_key)
    
    @property
    def parent_id_attr_name(self):
        return '{}_id'.format(self.parent_key)
    
    @property
    def parent_tablename_attr_name(self):
        return '{}_tablename'.format(self.parent_key)
    
    def get_childthing_descriptor(self, parent):
        return getattr(type(parent), self.childthing_key)
    
    def get_parent_descriptor(self, child):
        return getattr(type(child), self.parent_key)
    
    def get_attr_name_key(self, owner):
        """ Get the attribute name of this descriptor instance from
            'owner.__dict__'.
            
            Find this instance in the owner's '__dict__' values. """
        for ikey, ivalue in owner.__dict__.items():
            if ivalue is self:
                return ikey
    
    def expire_related(self, instance, attr_name):
        try:
            delattr(instance, attr_name)
        except AttributeError:
            pass
    
    def propagate_session_add(self, instance_a, instance_b):
        """ If either instance is in the session, add the other to the
            session also. """
        instances = (instance_a, instance_b)
        
        if None in instances:
            return
        
        s = DBSession()
        for item in instances:
            if item in s:
                s.add_all(instances)

class MultiClassParent(MultiClassRelationship):
    def __init__(self, *, backref, parent_classes):
        self.childthing_key = backref
        self.parent_classes = parent_classes
    
    def _setup(self, owner, global_dict):
        """ Get 'parent_key' from class attribute name.
            Convert string 'class' values to actual class objects. """
        self.parent_key = self.get_attr_name_key(owner)
        
        self.parent_classes = [
            global_dict[item] if isinstance(item, str) else item
            for item in self.parent_classes
            ]
        
        self.parent_classes_by_tablename = {
            item.__tablename__: item
            for item in self.parent_classes
            }
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        return self.get_parent_obj(instance)
    
    def __set__(self, instance, value):
        child = instance
        new_parent = value
        
        old_parent = self.get_parent_obj(child)
        
        if new_parent is old_parent:
            return
        
        if new_parent is None:
            pass
        elif type(new_parent) not in self.parent_classes:
            raise RelatedObjectTypeError(
                "Ineligible parent object type: '{}'"
                .format(type(new_parent).__name__)
                )
        
        # Remove from previous parent object's childthing descriptor.
        if old_parent is not None:
            old_childthing_descriptor = self.get_childthing_descriptor(old_parent)
            old_childthing_descriptor.unset_child_obj(old_parent, child)
        
        # Add to new parent object's childthing descriptor.
        if new_parent is not None:
            new_childthing_descriptor = self.get_childthing_descriptor(new_parent)
            new_childthing_descriptor.set_child_obj(new_parent, child)
        
        # Make the change persistent.
        self.set_parent_obj(child, new_parent)
    
    def get_parent_obj(self, instance):
        if not hasattr(instance, self.parent_obj_attr_name):
            self.initialize_related(instance)
        return getattr(instance, self.parent_obj_attr_name)
    
    def set_parent_obj(self, instance, parent_obj):
        if parent_obj is None:
            parent_id, parent_tablename = None, None
        else:
            parent_id = parent_obj.id
            parent_tablename = parent_obj.__tablename__
        
        # Set column values.
        setattr(instance, self.parent_id_attr_name, parent_id)
        setattr(instance, self.parent_tablename_attr_name, parent_tablename)
        
        # Stash parent object.
        setattr(instance, self.parent_obj_attr_name, parent_obj)
        
        if parent_obj is None:
            return
        
        self.propagate_session_add(parent_obj, instance)
    
    def query_for_parent(self, instance):
        parent_tablename = getattr(instance, self.parent_tablename_attr_name)
        parent_id = getattr(instance, self.parent_id_attr_name)
        
        """ It is necessary at this point to return if both 'parent_tablename'
            and 'parent_id' are not provided. At some point during the
            application setup, all of the attributes in every mapper class are
            accessed. If DBSession() is called here during application setup, it
            will cause setup to break. Checking for these values avoids this
            situation. """
        if parent_id is None and parent_tablename is None:
            return None
        
        def raise_error(column_key, invalid_value):
            attr_name = getattr(self, '{}_attr_name'.format(column_key))
            raise ParentNotFoundError(
                "Invalid '{}' value: {}".format(attr_name, invalid_value)
                )
        
        if parent_id is None:
            raise_error('parent_id', parent_id)
        if parent_tablename is None:
            raise_error('parent_tablename', parent_tablename)
        
        try:
            parent_class = self.parent_classes_by_tablename[parent_tablename]
        except KeyError:
            raise_error('parent_tablename', parent_tablename)
        
        parent_obj = DBSession().query(parent_class).get(parent_id)
        
        if parent_obj is None:
            raise ParentNotFoundError(
                "Parent entry not found in table '{}'; ID value: {}"
                .format(parent_tablename, parent_id)
                )
        
        return parent_obj
    
    def initialize_related(self, instance):
        parent_obj = self.query_for_parent(instance)
        
        setattr(instance, self.parent_obj_attr_name, parent_obj)
    
    def expire_related(self, instance):
        super().expire_related(instance, self.parent_obj_attr_name)
    
    def get_attribute_object(self, instance):
        return getattr(instance, self.parent_obj_attr_name)

class MonoClassChildthingDescriptor(MultiClassRelationship):
    """ Parent class for 'MultiClass' child descriptors. """
    def __init__(self, *, backref, child_class):
        self.parent_key = backref
        self.child_class = child_class
    
    def _setup(self, owner, global_dict):
        """ Get 'childthing_key' from class attribute name.
            Convert string 'class' values to actual class objects. """
        self.childthing_key = self.get_attr_name_key(owner)
        
        if isinstance(self.child_class, str):
            self.child_class = global_dict[self.child_class]
    
    def __get__(self, instance, owner):
        if not instance:
            return self
        
        if not hasattr(instance, self.childthing_obj_attr_name):
            self.initialize_related(instance)
        
        return getattr(instance, self.childthing_obj_attr_name)
    
    def query_for_children(self, parent):
        filters = {
            self.parent_id_attr_name: parent.id,
            self.parent_tablename_attr_name: parent.__tablename__,
            }
        return (
            DBSession().query(self.child_class)
            .filter_by(**filters)
            )
    
    def set_parent_of_child(self, child, parent):
        parent_descriptor = self.get_parent_descriptor(child)
        parent_descriptor.set_parent_obj(child, parent)
    
    def expire_related(self, instance):
        super().expire_related(instance, self.childthing_obj_attr_name)
    
    def verify_child_type(self, child):
        if type(child) is not self.child_class:
            raise RelatedObjectTypeError(
                "Ineligible child object type: '{}'"
                .format(type(child).__name__)
                )
    
    def get_attribute_object(self, instance):
        return getattr(instance, self.childthing_obj_attr_name)

class MonoClassChild(MonoClassChildthingDescriptor):
    def __init__(self, *, required=False, **kwargs):
        super().__init__(**kwargs)
        self.required = required
    
    def __set__(self, instance, value):
        parent = instance
        new_child = value
        
        old_child = self.get_child(parent)
        
        if new_child is old_child:
            return
        
        if new_child is not None:
            self.verify_child_type(new_child)
        
        if old_child is not None:
            self.set_parent_of_child(old_child, None)
        
        if new_child is not None:
            self.set_parent_of_child(new_child, parent)
        
        self.set_child_obj(parent, new_child)
    
    def set_child_obj(self, instance, child):
        setattr(instance, self.childthing_obj_attr_name, child)
        
        self.propagate_session_add(instance, child)
    
    def unset_child_obj(self, instance, child):
        setattr(instance, self.childthing_obj_attr_name, None)
    
    def get_child(self, instance):
        return self.__get__(instance, type(instance))
    
    def query_for_child(self, instance):
        try:
            return self.query_for_children(instance).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return None
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise MultipleChildrenError(
                "More than one result found when querying for child entry."
                )
    
    def initialize_related(self, instance):
        child = self.query_for_child(instance)
        
        setattr(instance, self.childthing_obj_attr_name, child)

class MonoClassChildrenCollection(SideEffectSet):
    def _setup(self, parent_obj, descriptor):
        """ This method cannot be '__init__', because sets use the class
            constructor during some set operations. """
        self.parent_obj = parent_obj
        self.descriptor = descriptor
        
        """ It is necessary at this point to return if 'parent_obj.id' is not
            provided. At some point during the application setup, all of the
            attributes in every mapper class are accessed. If DBSession() is
            called here during application setup, it will cause setup to break.
            Checking for this value avoids this situation. """
        if not parent_obj.id:
            return
        
        children = descriptor.query_for_children(parent_obj).all()
        
        if children:
            # Bypass side effects when initializing.
            set.update(self, children)
    
    def _add_element(self, child):
        self.descriptor.verify_child_type(child)
        self.descriptor.set_parent_of_child(child, self.parent_obj)
    
    def _remove_element(self, child):
        self.descriptor.set_parent_of_child(child, None)

class MonoClassChildren(MonoClassChildthingDescriptor):
    def __set__(self, instance, value):
        children = self.get_children(instance)
        children.replace(value)
    
    def set_child_obj(self, instance, child):
        """ Bypass side effects. """
        children = self.get_children(instance)
        set.add(children, child)
        
        self.propagate_session_add(instance, child)
    
    def unset_child_obj(self, instance, child):
        """ Bypass side effects. """
        children = self.get_children(instance)
        set.remove(children, child)
    
    def get_children(self, instance):
        return self.__get__(instance, type(instance))
    
    def initialize_related(self, instance):
        children = MonoClassChildrenCollection()
        children._setup(instance, self)
        
        setattr(instance, self.childthing_obj_attr_name, children)

class MultiClassRelationshipSetupManager(object):
    """ This class performs setup operations for the 'MultiClassRelationship'
        ('MCR' for short) descriptors.
        
        MCR parents and children both expire related objects.
        
        MCR parents attach children to the session.
        
        Note that all 'expire' listeners must check 'target' is not 'None'
        because of an unpredictable bug where 'target' would sometimes be
        'None'. I don't know why this would happen, and I was unable to
        predictably reproduce this situation. This should be investigated
        further. """
    
    def __init__(self, global_dict):
        self.child_classes = {}
        self.parent_classes = {}
        self.parent_single_child_classes = {}
        # 'all_classes' includes both 'parent' and 'child' classes.
        self.all_classes = {}
        
        for item in global_dict.values():
            child_relationships = []
            single_child_relationships = []
            parent_relationships = []
            all_relationships = []
            
            if not inspect.isclass(item):
                continue
            if not issubclass(item, SQLAlchemyBase):
                continue
            
            for iattr in item.__dict__.values():
                if isinstance(iattr, MultiClassParent):
                    parent_relationships.append(iattr)
                elif isinstance(iattr, MonoClassChildthingDescriptor):
                    child_relationships.append(iattr)
                    if isinstance(iattr, MonoClassChild):
                        single_child_relationships.append(iattr)
                else:
                    continue
                all_relationships.append(iattr)
            
            if parent_relationships:
                self.child_classes[item] = tuple(parent_relationships)
            if child_relationships:
                self.parent_classes[item] = tuple(child_relationships)
            if single_child_relationships:
                self.parent_single_child_classes[item] = \
                    tuple(single_child_relationships)
            if all_relationships:
                self.all_classes[item] = tuple(all_relationships)
    
    def child_after_flush_listener(self, session, flush_context):
        classinfo = tuple(self.child_classes.keys())
        
        for item in session.checker.get_all(classinfo):
            session.checker.ids['multi_class_children'][type(item)].add(item.id)
    
    def child_before_commit_listener(self, session):
        def checking_routine(item, parent_relationships=[]):
            for descriptor in parent_relationships:
                descriptor.query_for_parent(item)
        
        pairs = session.checker.ids['multi_class_children'].items()
        
        for iclass, iids_set in pairs:
            parent_relationships = self.child_classes[iclass]
            
            session.checker.pre_commit_check(
                iclass,
                iids_set,
                checking_routine,
                parent_relationships
                )
    
    def parent_single_child_after_flush_listener(self, session, flush_context):
        classinfo = tuple(self.parent_single_child_classes.keys())
        
        for item in session.checker.get_all(classinfo):
            session.checker.ids[
                'multi_class_parents_single_child'
                ][type(item)].add(item.id)
    
    def parent_single_child_before_commit_listener(self, session):
        """ For each instance with a 'MonoClassChild' descriptor:
            
            - Call 'get_child' on that instance.
                This raises an exception if more than one child has been assigned
                to a single parent.
            
            - If the child is 'required', and no child is assigned to the
              parent, raise an error.
            
            """
        def checking_routine(item, child_relationships=[]):
            for descriptor in child_relationships:
                child = descriptor.get_child(item)
                
                if descriptor.required and child is None:
                    raise RequiredChildError("No child assigned to parent.")
        
        pairs = session.checker.ids['multi_class_parents_single_child'].items()
        
        for iclass, iids_set in pairs:
            child_relationships = self.parent_single_child_classes[iclass]
            
            session.checker.pre_commit_check(
                iclass,
                iids_set,
                checking_routine,
                child_relationships
                )
    
    class ExpireListener(object):
        """ All expire related. """
        def __init__(self, relationship_objs):
            self.relationship_objs = relationship_objs
        
        def __call__(self, target, attrs):
            if target is None or attrs is not None:
                return
            
            for item in self.relationship_objs:
                item.expire_related(target)
    
    def after_attach_listener(self, session, instance):
        """ Parents attach children. Children attach parents. """
        try:
            relationship_objs = self.all_classes[type(instance)]
        except KeyError:
            return
        
        for idescriptor in relationship_objs:
            try:
                related_obj = idescriptor.get_attribute_object(instance)
            except AttributeError:
                continue
            
            if isinstance(
                related_obj,
                (collections.abc.Sequence, collections.abc.Set),
                ):
                session.add_all(related_obj)
            elif related_obj is not None:
                session.add(related_obj)
    
    @classmethod
    def setup(cls, global_dict):
        """ This method must be called after all 'model' classes have been
            declared. It is best to call this method at the very end of the
            'model' module. """
        manager = cls(global_dict)
        
        # Call '_setup' on all descriptors.
        for iclass, irelationships in manager.all_classes.items():
            for irelationship in irelationships:
                irelationship._setup(iclass, global_dict)
        
        # Session checker id collections.
        SessionPreCommitChecker.id_collections[
            'multi_class_children'
            ] = make_defaultdict_of_set
        SessionPreCommitChecker.id_collections[
            'multi_class_parents_single_child'
            ] = make_defaultdict_of_set
        
        # Add 'after_flush', 'before_commit' listeners.
        for item in ['child', 'parent_single_child']:
            for ievent in ['after_flush', 'before_commit']:
                listener_attr_name = '{}_{}_listener'.format(
                    item, ievent,
                    )
                listener = getattr(manager, listener_attr_name)
                sqlalchemy.event.listen(DBSession, ievent, listener)
        
        # Add 'expire' listeners.
        for item, relationship_objs in manager.all_classes.items():
            listener = manager.ExpireListener(relationship_objs)
            sqlalchemy.event.listen(item, 'expire', listener)
        
        # Add 'attach' listener.
        sqlalchemy.event.listen(
            DBSession,
            'after_attach',
            manager.after_attach_listener,
            )



# ------------------------------ Nodelike ------------------------------

class NodeLike(object):
    """ Superclass for all objects with node-like behavior.
        
        Subclasses must have the following columns:
        id                  UUID
        parent_id           UUID
        parent_tablename    String
        
        Subclasses must implement children-nodelike relationship.
        
        Accounts are strictly-defined nodes. """
    
    def delete(self):
        self.parent = None
        delete_or_expunge(self)
    
    def check_for_loop(
        self,
        ok_nodes_set=set(),
        loop_start=None,
        max_recursion_depth=128,
        recursion_countdown=None,
        ):
        """ Check that this node is not part of a dependency loop. This means:
            check that loop_start is not a descendant of itself.
            
            If a loop is detected, a NodeLoopError is raised.
            
            .check_for_loop() is called recursively on each parent until a
            parent that is not a NodeLike instance is found.
            
            ok_nodes_set is a set of NodeLikes that have already been checked.
            
            If this node's parent does not raise an error, then this node adds
            itself to ok_nodes_set and returns ok_nodes_set. Since this node is
            OK, then all of its children must be OK as well; this sets off a
            cascade which adds all of this node's children to ok_nodes_set. In
            this way the checking routine is mininimized. """
        
        """ Check that the parent is both a NodeLike instance, and that the
            parent is not in ok_nodes_set. If either of these conditions are
            met, add this instance to ok_nodes_set and return ok_nodes_set. """
        for i in range(1):
            if self.parent in ok_nodes_set:
                continue
            if not isinstance(self.parent, NodeLike):
                continue
            break
        else:
            ok_nodes_set.add(self)
            return ok_nodes_set
        
        if recursion_countdown is None:
            recursion_countdown = max_recursion_depth
        
        if loop_start is None:
            loop_start = self
        
        if recursion_countdown < 1:
            raise NodeLoopError(
                "NodeLike tree depth exceeded maximum recursion depth for "
                "loop-checking routine: {}".format(str(max_recursion_depth))
                )
        
        if self.parent is loop_start:
            raise NodeLoopError(
                "NodeLike dependency loop detected. Type: '{}'; Depth: {}"
                .format(
                    type(self).__name__,
                    str(max_recursion_depth - recursion_countdown)
                    )
                )
        
        ok_nodes_set = self.parent.check_for_loop(
            ok_nodes_set=ok_nodes_set,
            loop_start=loop_start,
            recursion_countdown=(recursion_countdown - 1),
            max_recursion_depth=max_recursion_depth,
            )
        
        """ If no error was raised, then this instance is OK. Add this instance
            to ok_nodes_set and return ok_nodes_set. """
        ok_nodes_set.add(self)
        return ok_nodes_set

class NodeLikeSetupManager(object):
    @staticmethod
    def before_commit_listener(session):
        def checking_routine(item, ok_nodes_set=set()):
            ok_nodes_set = item.check_for_loop(ok_nodes_set)
            return [ok_nodes_set]
        
        for iclass, iids_set in session.checker.ids['nodelike'].items():
            session.checker.pre_commit_check(iclass, iids_set, checking_routine)
    
    @staticmethod
    def after_flush_listener(session, flush_context):
        """ Store account transaction ID's that need to be checked before
            'commit'. """
        for item in session.checker.get_all(NodeLike):
            session.checker.ids['nodelike'][type(item)].add(item.id)
    
    @classmethod
    def setup(cls):
        SessionPreCommitChecker.id_collections['nodelike'] = \
            make_defaultdict_of_set
        
        for ievent in ['after_flush', 'before_commit']:
            listener = getattr(cls, '{}_listener'.format(ievent))
            sqlalchemy.event.listen(DBSession, ievent, listener)







