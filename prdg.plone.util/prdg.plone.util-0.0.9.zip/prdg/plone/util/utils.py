from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, getUtility, subscribers
from OFS.Image import File, Image
from Acquisition import aq_inner, aq_parent
from plone.portlets.interfaces import (IPortletManager, 
    IPortletAssignmentMapping)

try:
    from collective.wtf.interfaces import ISanityChecker
except ImportError:
    ISanityChecker = None    

def get_workflow_info(obj):
    """
    Return: the workflow info of an object as a dict or None if the object
        does not have a workflow.
        """    
    wf = getToolByName(obj, 'portal_workflow')
    workflows = wf.getWorkflowsFor(obj)
    if not workflows:
        return None
    
    workflow = workflows[0]
    return wf.getStatusOf(workflow.id, obj)

def get_workflow_state(obj):
    """
    Return: the workflow state of an object as an string or None if the
        object does not have a workflow.
    """
    wf_info = get_workflow_info(obj)
    if not wf_info:
        return None
    
    return wf_info['review_state']

def get_workflow_transitions(obj, dest, source=None):
    """
    Return: a set containing the workflow transitions from the source to the 
    dest state on the given object. If source is ommited then the current
    state is used.
    """
    wf = getToolByName(obj, 'portal_workflow')
    workflow = wf.getWorkflowsFor(obj)[0]
    
    if not source:
        source = wf.getStatusOf(workflow.id, obj)['review_state']
        
    source_state = getattr(workflow.states, source)
    
    return set(
        t.getId() 
        for t in workflow.transitions.objectValues() 
        if t.getId() in source_state.getTransitions()
        if t.new_state_id == dest        
    )
    
def ensure_workflow_state(obj, state, comment=None):
    """
    Tries to do a transition from the current state to `state`. If obj is 
    already in the given state then nothing is done. If `state` is None or other
    false value then nothing is done.
    
    Return: the transition executed or `None` if the object is already in the desired state.
    
    Raise: RuntimeError if cannot find a transition to `state`. 
    """    
    if not state:
        return
           
    if state != get_workflow_state(obj):        
        transitions = get_workflow_transitions(obj, dest=state)
        if not transitions:
            raise RuntimeError(
                'Cannot find a transition to "%s" for the object: %s'
                % (state, obj)
            )
        
        wf = getToolByName(obj, 'portal_workflow')
        kwargs = {'comment': comment} if comment else {}
        transition = transitions.pop()
        wf.doActionFor(obj, transition, **kwargs)
        
        return transition      
    
def get_portlet_assignments(context, manager_name):
    """
    Return: an IPortletAssignmentMapping for the given context. manager_name can
        be 'plone.rightcolumn', 'plone.leftcolumn' or any other portlet manager
        name.    
    """
    manager = getUtility(IPortletManager, name=manager_name)    
    return getMultiAdapter((context, manager,), IPortletAssignmentMapping)    
    
def remove_all_portlets(context, manager_name):
    """
    Remove all portlets from a portlet manager. manager_name can
        be 'plone.rightcolumn', 'plone.leftcolumn' or any other portlet manager
        name.        
    """
    assignments = get_portlet_assignments(context, manager_name)
    for a in assignments:
        del assignments[a]
        
def ofs_file_equal(file1, file2):
    """
    Return: True if and only if the two given OFS.File.File objects are
    equal.
    """
    return (
        (
            (not file1) and (not file2)
        ) or (
            (file1.filename == file2.filename)
            and (str(file1.data) == str(file2.data))
            and (file1.getContentType() == file2.getContentType())
        )   
    )

def ofs_file_copy(f, factory=File):
    new_f = factory(
        id=f.getId(),
        title=f.title,
        file=(f.data and str(f.data)) or '',
        content_type=f.getContentType() or '',
        precondition=f.precondition or '',        
    )
    new_f.filename = f.filename
    
    return new_f

def ofs_image_copy(i):
    return ofs_file_copy(i, Image)

def relativize_path(base_path, full_path):
    """
    Arguments:
    base_path, full_path -- Tuples representing paths.
    
    Return: full_path relative to base_path.
    """
    return full_path[len(base_path):]

def change_base_path(old_base_path, new_base_path, full_path):
    return new_base_path + relativize_path(old_base_path, full_path)

def sanity_check_workflow(wf_definition):
    """
    Check the `wf_definition` for common errors. Return a sequence of
    error messages or an empty sequence.
    """
    if ISanityChecker is None:
        raise RuntimeError(
            'collective.wtf could not be found. You must have it on your '
            'PYTHONPATH in order to use this function.'
        )
    
    messages = []
    for checker in subscribers((wf_definition,), ISanityChecker):
        new_messages = checker()
        if new_messages:
            messages += new_messages
    return messages

def add_new_view(portal_type_obj, template, default=True):
    """
    Add a new view template for a content type.
    
    Arguments:
    portal_type_obj -- An FTI, i.e an object inside the `portal_types` tool.
    template -- The name of a view template.
    default -- Optional. Should be set to the default view ? Defaults to True.
    """
    views = list(portal_type_obj.view_methods)
    views.append(template)
    portal_type_obj.view_methods = views
    
    if default:
        portal_type_obj.default_view = template
        portal_type_obj.immediate_view    

def change_allowed_types(portal_type_obj, to_add=set(), to_remove=set()):
    """
    Change the allowed content types for a content type.
    
    Arguments:
    portal_type_obj -- An FTI, i.e an object inside the `portal_types` tool.
    to_add -- A set containing portal type names to add.
    to_remove -- A set containing portal type names to remove.    
    """
    allowed_types = set(portal_type_obj.allowed_content_types)
    allowed_types -= to_remove
    allowed_types |= to_add
    portal_type_obj.allowed_content_types = tuple(allowed_types)
    
def ancestor_providing(obj, interface):
    """
    Return: the nearest containment ancestor of `obj` providing `interface`. If
        `obj` provide it then return `obj`. Return `None` if no such ancestor
        is found.
    """
    if interface.providedBy(obj):
        return obj
    
    parent = aq_parent(aq_inner(obj))
    if parent is None:
        return None
    
    return ancestor_providing(parent, interface) 

def change_lines_property(sheet, property_name, to_add=[], to_remove=[]):
    """Add and remove lines from a lines property inside a property sheet."""
    lines = set(getattr(sheet, property_name))
    lines |= set(to_add)
    lines -= set(to_remove)
    
    setattr(
        sheet, 
        property_name, 
        list(lines)
    )   
    
 
