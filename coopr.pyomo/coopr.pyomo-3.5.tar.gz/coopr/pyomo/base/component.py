#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Component', 'ComponentUID', 'cname']

from weakref import ref as weakref_ref
import sys
from six import iteritems
from coopr.pyomo.base.plugin import register_component
from coopr.pyomo.base.misc import tabular_writer


try:
    basestring
except:
    basestring = str

def _cname_index_generator(idx):
    if idx.__class__ is tuple:
        return "[" + ",".join(str(i) for i in idx) + "]"
    else:
        return "[" + str(idx) + "]"


def cname(component, index=None, fully_qualified=False):
    base = component.cname(fully_qualified=fully_qualified)
    if index is None:
        return base
    else:
        if index not in component.index_set():
            raise KeyError( "Index %s is not valid for component %s"
                            % (index, component.cname(True)) )
        return base + _cname_index_generator( index )


class Component(object):
    """
    This is the base class for all Pyomo modeling components.

    Constructor arguments:
        ctype           The class type for the derived subclass
        doc             A text string describing this component
        name            A name for this component

    Public class attributes:
        doc             A text string describing this component

    Private class attributes:
         _active        A boolean that is true if this component will be 
                            used in model operations
        _constructed    A boolean that is true if this component has been
                            constructed
        _parent         A weakref to the parent block that owns this component
        _type           The class type for the derived subclass
    """

    def __init__ (self, **kwds):
        #
        # Get arguments
        #
        self.doc   = kwds.pop('doc', None)
        self.name  = kwds.pop('name', str(type(self).__name__)) # "{unnamed}"
        self._type = kwds.pop('ctype', None)
        if kwds:
            raise ValueError(
                "Unexpected keyword options found while constructing '%s':\n\t%s"
                % ( type(self).__name__, ','.join(sorted(kwds.keys())) ))
        #
        # Verify that ctype has been specified.
        #
        if self._type is None:
            raise DeveloperError("Must specify a class for the component type!")
        #
        self._constructed = False
        self._parent = None    # Must be a weakref
        self._active = True

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value):
        raise AttributeError("Assignment not allowed. Use the (de)activate method")

    def activate(self):
        """Set the active attribute to True"""
        self._active=True

    def deactivate(self):
        """Set the active attribute to False"""
        self._active=False

    def __getstate__(self):
        """
        This method must be defined to support pickling because this class
        owns weakrefs for '_parent'.
        """
        # Nominally, __getstate__() should return:
        #
        # state = super(Class, self).__getstate__()
        # for i in Class.__dict__:
        #     state[i] = getattr(self,i)
        # return state
        #
        # Hoewever, in this case, the (nominal) parent class is
        # 'object', and object does not implement __getstate__.  Since
        # super() doesn't actually return a class, we are going to check
        # the *derived class*'s MRO and see if this is the second to
        # last class (the last is always 'object').  If it is, then we
        # can allocate the state dictionary.  If it is not, then we call
        # the super-class's __getstate__ (since that class is NOT
        # 'object').
        if self.__class__.__mro__[-2] is Component:
            state = dict(self.__dict__)
        else:
            state = super(Component,self).__getstate__()
            for key,val in iteritems(self.__dict__):
                if key not in state:
                    state[key] = val
        
        if self._parent is not None:
            state['_parent'] = self._parent()
        return state

    def __setstate__(self, state):
        """
        This method must be defined to support pickling because this class
        owns weakrefs for '_parent'.
        """
        if state['_parent'] is not None and \
                type(state['_parent']) is not weakref_ref:
            state['_parent'] = weakref_ref(state['_parent'])
        # Note: our model for setstate is for derived classes to modify
        # the state dictionary as control passes up the inheritance
        # hierarchy (using super() calls).  All assignment of state ->
        # object attributes is handled at the last class before 'object'
        # (which may -- or may not (thanks to MRO) -- be here.
        if self.__class__.__mro__[-2] is Component:
            for key, val in iteritems(state):
                # Note: per the Python data model docs, we explicitly
                # set the attribute using object.__setattr__() instead
                # of setting self.__dict__[key] = val.
                object.__setattr__(self, key, val)
        else:
            return super(Component,self).__setstate__(state)

    def __str__(self):
        return self.cname(True)

    def to_string(self, ostream=None, verbose=None, precedence=0):
        if ostream is None:
            ostream = sys.stdout
        ostream.write(self.__str__())

    def type(self):
        """Return the class type for this component"""
        return self._type

    def construct(self, data=None):                     #pragma:nocover
        """API definition for constructing components"""
        pass

    def is_constructed(self):                           #pragma:nocover
        """Return True if this class has been constructed"""
        return self._constructed

    def reconstruct(self, data=None):
        self._constructed = False
        self.construct(data=data)

    def valid_model_component(self):
        """Return True if this can be used as a model component."""
        return True

    def pprint(self, ostream=None, verbose=False, prefix=""):
        """Print component information"""
        if ostream is None:
            ostream = sys.stdout
        tab="    "
        ostream.write(prefix+self.cname()+" : ")
        if self.doc is not None:
            ostream.write(self.doc+'\n'+prefix+tab)

        _attr, _data, _header, _fcn = self._pprint()

        ostream.write(", ".join("%s=%s" % (k,v) for k,v in _attr))
        ostream.write("\n")
        if not self._constructed:
            ostream.write(prefix+tab+"Not constructed\n")
            return

        tabular_writer( ostream, prefix+tab, _data, _header, _fcn )

    def component(self):
        return self

    def parent(self):
        if self._parent is None:
            return None
        else:
            return self._parent()

    def model(self):
        ans = self.parent()
        if ans is None:
            return None
        while ans.parent() is not None:
            ans = ans.parent()
        return ans

    def cname(self, fully_qualified=False, name_buffer=None):
        if fully_qualified and self.parent() != self.model():
            return self.parent().cname(fully_qualified, name_buffer) \
                + "." + self.name
        return self.name

class ComponentData(object):

    __slots__ = ( '_component', )

    def __init__(self, owner):
        # ComponentData objects are typically *private* objects for
        # indexed / sparse indexed components.  As such, the (derived)
        # class needs to make sure that the owning component is *always*
        # passed as the owner (and that owner is never None).  While we
        # used to check for this, removing the check significantly
        # speeds things up.
        self._component = weakref_ref(owner)

    def __getstate__(self):
        # Nominally, __getstate__() should return:
        #
        # state = super(Class, self).__getstate__()
        # for i in Class.__slots__:
        #    state[i] = getattr(self,i)
        # return state
        #
        # Hoewever, in this case, the (nominal) parent class is
        # 'object', and object does not implement __getstate__.  Since
        # super() doesn't actually return a class, we are going to check
        # the *derived class*'s MRO and see if this is the second to
        # last class (the last is always 'object').  If it is, then we
        # can allocate the state dictionary.  If it is not, then we call
        # the super-class's __getstate__ (since that class is NOT
        # 'object').
        #
        # Further, since there is only a single slot, and that slot
        # (_component) requires special processing, we will just deal
        # with it explicitly.  As _component is a weakref (not
        # pickable), so we need to resolve it to a concrete object.
        if self.__class__.__mro__[-2] is ComponentData:
            state = {}
        else:
            state = super(ComponentData,self).__getstate__()
        
        if self._component is None:
            state['_component'] = None
        else:
            state['_component'] = self._component()
        return state

    def __setstate__(self, state):
        # FIXME: We shouldn't have to check for weakref.ref here, but if
        # we don't the model cloning appears to fail (in the Benders
        # example)
        if state['_component'] is not None and \
                type(state['_component']) is not weakref_ref:
            state['_component'] = weakref_ref(state['_component'])

        # Note: our model for setstate is for derived classes to modify
        # the state dictionary as control passes up the inheritance
        # hierarchy (using super() calls).  All assignment of state ->
        # object attributes is handled at the last class before 'object'
        # (which may -- or may not (thanks to MRO) -- be here.
        if self.__class__.__mro__[-2] is ComponentData:
            for key, val in iteritems(state):
                # Note: per the Python data model docs, we explicitly
                # set the attribute using object.__setattr__() instead
                # of setting self.__dict__[key] = val.
                object.__setattr__(self, key, val)
        else:
            return super(ComponentData,self).__setstate__(state)

    def __str__(self):
        return self.cname(True)

    def to_string(self, ostream=None, verbose=None, precedence=0):
        if ostream is None:
            ostream = sys.stdout
        ostream.write(self.__str__())

    def component(self):
        if self._component is None: 
            return None
        return self._component()

    # returns the index of this ComponentData instance relative
    # to the parent component index set. None is returned if 
    # this instance does not have a parent component, or if
    # - for some unknown reason - this instance does not belong
    # to the parent component's index set. not intended to be
    # a fast method - should be used rarely, primarily in 
    # cases of label formulation.
    def index(self):
        self_component = self.component()
        if self_component is None:
            return None
        for idx, component_data in self_component.iteritems():
            if id(component_data) == id(self):
                return idx
        return None
        
    def parent(self):
        ans = self.component()
        if ans is None:
            return None
        # Directly call the Component's model() to prevent infinite
        # recursion for singleton objects.
        if ans is self:
            return super(ComponentData, ans).parent()
        else:
            return ans.parent()

    def cname(self, fully_qualified=False, name_buffer=None):
        c = self.component()
        if c is self:
            return super(ComponentData, self).cname(fully_qualified, name_buffer)

        base = c.cname(fully_qualified, name_buffer)
        if name_buffer is not None:
            if id(self) in name_buffer:
                # should we delete the entry to save mamory?  JDS:
                # probably not, because for nested blocks, we would hit
                # this part of the code numerous times.
                return name_buffer[id(self)]
            for idx, obj in iteritems(c._data):
                name_buffer[id(obj)] = base + _cname_index_generator(idx)
            if id(self) in name_buffer:
                return name_buffer[id(self)]
        else:
            for idx, obj in iteritems(c._data):
                if obj is self:
                    return base + _cname_index_generator(idx)

        raise RuntimeError("Fatal error: cannot find the component data in "
                           "the owning component's _data dictionary.")

    def model(self):
        ans = self.component()
        if ans is None:
            return None
        # Directly call the Component's model() to prevent infinite
        # recursion for singleton objects.
        if ans is self:
            return super(ComponentData, ans).model()
        else:
            return ans.model()


class ActiveComponentData(ComponentData):

    __slots__ = ( '_active', )

    def __init__(self, owner):
        super(ActiveComponentData, self).__init__(owner)
        #TODO: If we construct a new ActiveComponentData member on a deactivated
        #      Component do we need to inform the deactivated Component that it is now 
        #      active (as in the activate() method), or do we need to inherit the current
        #      active status of the owning component?
        self._active = True

    def __getstate__(self):
        """
        This method must be defined because this class uses slots.
        """
        result = super(ActiveComponentData, self).__getstate__()
        for i in ActiveComponentData.__slots__:
            result[i] = getattr(self, i)
        return result

    # Since this class requires no special processing of the state
    # dictionary, it does not need to implement __setstate__()
    #def __setstate__(self, state):
    #    pass

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value):
        raise AttributeError("Assignment not allowed. Use the (de)activate method")

    def activate(self):
        """Set the active attribute to True"""
        self._active = self.component()._active = True

    def deactivate(self):
        """Set the active attribute to False"""
        #
        # *** NOTE ***: 
        #
        # It's possible to end up in a state where the parent Component
        # has _active=True but all ComponentData have _active=False. In
        # my opinion, this is okay, and will be corrected the next time
        # activate() is called anywhere (on Component or ComponentData).
        # The important thing to avoid is the situation where one or
        # more ComponentData are active, but the parent Component claims
        # active=False. This class structure is designed to prevent this
        # situation.
        #
        self._active = False

class ComponentUID(object):
    __slots__ = ( '_cids', )
    tList = [ int, str ]
    tKeys = '#$'
    tDict = {} # ...initialized below

    def __init__(self, component, cuid_buffer=None):
        if isinstance(component, basestring):
            self._cids = tuple( self.parse_cuid(component) )
        else:
            self._cids = tuple( self._generate_cuid(component, cuid_buffer) )

    def __str__(self):
        a = ""
        for name, args, types in reversed(self._cids):
            if a:
                a += '.' + name
            else:
                a = name
            if types is None:
                a += '[**]'
                continue
            if len(args) == 0:
                continue
            a += '['+','.join(str(x) or '*' for x in args) + ']'
        return a

    def __repr__(self):
        a = ""
        for name, args, types in reversed(self._cids):
            if a:
                a += '.' + name
            else:
                a = name
            if types is None:
                a += ':**'
                continue
            if len(args) == 0:
                continue
            a += ':'+','.join( (types[i] if types[i] not in '.' else '')+str(x) 
                               for i,x in enumerate(args) )
        return a

    def __getstate__(self):
        return dict((x,getattr(val,x)) for x in ComponentUID.__slots__)

    def __setstate__(self, state):
        for key, val in iteritems(state):
            setattr(self,key,val) 

    # Define all comparison operators using the underlying tuple's
    # comparison operators. We will be lazy and assume that the other is
    # a CUID.
    def __hash__(self):
        return self._cids.__hash__()
    def __lt__(self, other):
        try:
            return self._cids.__lt__(other._cids)
        except AttributeError:
            return self._cids.__lt__(other)
    def __le__(self, other):
        try:
            return self._cids.__le__(other._cids)
        except AttributeError:
            return self._cids.__le__(other)
    def __gt__(self, other):
        try:
            return self._cids.__gt__(other._cids)
        except AttributeError:
            return self._cids.__gt__(other)
    def __ge__(self, other):
        try:
            return self._cids.__ge__(other._cids)
        except AttributeError:
            return self._cids.__ge__(other)
    def __eq__(self, other):
        try:
            return self._cids.__eq__(other._cids)
        except AttributeError:
            return self._cids.__eq__(other)
    def __ne__(self, other):
        try:
            return self._cids.__ne__(other._cids)
        except AttributeError:
            return self._cids.__ne__(other)

    def _partial_cuid_from_index(self, idx):
        tDict = ComponentUID.tDict
        if idx.__class__ is tuple:
            return ( idx, ''.join(tDict.get(type(x), '?') for x in idx) )
        else:
            return ( (idx,), tDict.get(type(idx), '?') )

    def _generate_cuid(self, component, cuid_buffer=None):
        model = component.model()
        tDict = ComponentUID.tDict
        if not hasattr(component, '_component'):
            yield ( component.cname(), '**', None )
            component = component.parent()
        while component is not model:
            c = component.component()
            if c is component:
                yield ( c.cname(), tuple(), '' )
            elif cuid_buffer is not None:
                if id(self) not in cuid_buffer:
                    for idx, obj in iteritems(c._data):
                        if idx.__class__ is tuple:
                            cuid_buffer[id(obj)] = \
                                self._partial_cuid_from_index(idx)
                yield (c.cname(),) + cuid_buffer[id(self)]
            else:
                for idx, obj in iteritems(c._data):
                    if obj is component:
                        yield (c.cname(),) + self._partial_cuid_from_index(idx)
                        break
            component = component.parent()

    def parse_cuid(self, label):
        cList = label.split('.')
        tKeys = ComponentUID.tKeys
        tDict = ComponentUID.tDict
        for c in reversed(cList):
            if c[-1] == ']':
                c_info = c[:-1].split('[',1)
            else:
                c_info = c.split(':',1)
            if len(c_info) == 1:
                yield ( c_info[0], tuple(), '' )
            else:
                idx = c_info[1].split(',')
                _type = ''
                for i, val in enumerate(idx):
                    if val == '*':
                        _type += '*'
                        idx[i] = ''
                    elif val[0] in tKeys:
                        _type += val[0]
                        idx[i] = tDict[val[0]](val[1:])
                    elif val[0] in  "\"'" and val[-1] == val[0]:
                        _type += ComponentUID.tDict[str]
                        idx[i] = val[1:-1]
                    else:
                        _type += '.'
                if len(idx) == 1 and idx[0] == '**':
                    yield ( c_info[0], '**', None )
                else:
                    yield ( c_info[0], tuple(idx), _type )


    # Return the (unique) component in the model.  If the CUID contains
    # a wildcard in the last component, then returns that component.  If
    # there are wildcards elsewhere (or the last component was a partial
    # slice), then returns None.  See list_components below.
    def find_component(self, model):
        obj = model
        for name, idx, types in reversed(self._cids):
            try:
                if len(idx) and idx != '**' and types.strip('*'):
                    obj = getattr(obj, name)[idx]
                else:
                    obj = getattr(obj, name)
            except KeyError:
                if '.' not in types:
                    return None
                tList = ComponentUID.tList
                def _checkIntArgs(_idx, _t, _i):
                    if _i == -1:
                        try:
                            return getattr(obj, name)[tuple(_idx)]
                        except KeyError:
                            return None
                    _orig = _idx[_i]
                    for _cast in tList:
                        try:
                            _idx[_i] = _cast(_orig)
                            ans = _checkIntArgs(_idx, _t, _t.find('.',_i+1))
                            if ans is not None:
                                return ans
                        except ValueError:
                            pass
                    _idx[_i] = _orig
                    return None
                obj = _checkIntArgs(list(idx), types, types.find('.'))
            except AttributeError:
                return None
        return obj

    def _list_components(self, _obj, cids):
        if not cids:
            yield _obj
            return

        name, idx, types = cids[-1]
        try:
            obj = getattr(_obj, name)
        except AttributeError:
            return
        if len(idx) == 0:
            for ans in self._list_components(obj, cids[:-1]):
                yield ans
        elif idx != '**' and '*' not in types and '.' not in types:
            try:
                obj = obj[idx]
            except KeyError:
                return
            for ans in self._list_components(obj, cids[:-1]):
                yield ans
        else:
            all =  idx == '**'
            tList = ComponentUID.tList
            for target_idx, target_obj in iteritems(obj._data):
                if not all and idx != target_idx:
                    _idx, _types = self._partial_cuid_from_index(target_idx)
                    if len(idx) != len(_idx):
                        continue
                    match = True
                    for j in range(len(idx)):
                        if idx[j] == _idx[j] or types[j] == '*':
                            continue
                        elif types[j] == '.':
                            ok = False
                            for _cast in tList:
                                try:
                                    if _cast(idx[j]) == _idx[j]:
                                        ok = True
                                        break
                                except ValueError:
                                    pass
                            if not ok:
                                match = False
                                break
                        else:
                            match = False
                            break
                    if not match:
                        continue
                for ans in self._list_components(target_obj, cids[:-1]):
                    yield ans

    def list_components(self, model):
        for ans in self._list_components(model, self._cids):
            yield ans

    def matches(self, component):
        tList = ComponentUID.tList
        for i, (name, idx, types) in enumerate(self._generate_cuid(component)):
            if i == len(self._cids):
                return False
            _n, _idx, _types = self._cids[i]
            if _n != name:
                return False
            if _idx == '**' or idx == _idx:
                continue
            if len(idx) != len(_idx):
                return False
            for j in range(len(idx)):
                if idx[j] == _idx[j] or _types[j] == '*':
                    continue
                elif _types[j] == '.':
                    ok = False
                    for _cast in tList:
                        try:
                            if _cast(_idx[j]) == idx[j]:
                                ok = True
                                break
                        except ValueError:
                            pass
                    if not ok:
                        return False
                else:
                    return False
        # Matched if all self._cids were consumed
        return i+1 == len(self._cids)

ComponentUID.tDict.update( (ComponentUID.tKeys[i], v) 
                           for i,v in enumerate(ComponentUID.tList) )
ComponentUID.tDict.update( (v, ComponentUID.tKeys[i]) 
                           for i,v in enumerate(ComponentUID.tList) )


class DeveloperError(Exception):
    """
    Exception class used to throw errors that result from
    programming errors, rather than user modeling errors (e.g., a
    component not declaring a 'ctype').
    """

    def __init__(self, val):
        self.parameter = val

    def __str__(self):                                  #pragma:nocover
        return repr(self.parameter)

