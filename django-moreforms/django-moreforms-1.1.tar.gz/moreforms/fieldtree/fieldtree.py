class FieldLeaf:
    
    def __init__(self, value, field_name,
                 children = (),
                 visible = True):
        
        """ A leaf is a node of the field decicion tree (the FieldTree).
        
        :param value: The regexp that the parent's posted value must match with
            in order to render the form.
            
        :param field_name: The name of the field that will be rendered/hidden.
        
        :param children: (OPTIONAL) A list of other FieldLeaves that will
            be used for recursion.
        """
        
        self.value = value
        self.field_name = field_name
        self.children = children
        self.visible = visible
        
        self.next_child = None
    
    def matches(self, request, value):
        """ A simple utility function to test whether a "posted" value matches
        the target regexp for a leaf.
        
        :param request: The HttpRequest object.
        
        :param value: The regexp string to test. e.g. '\d+'
        
        :return: True if the value does regex-match with the leaf's field in
            the form, False otherwise. Also return true if the value is none
            (e.g., for the root element).
        """
        if value is None:
            return True
        elif self.field_name not in request.POST:
            return False
        elif re.search(value, request.POST[self.field_name]) is not None:
            return True
        
        return False
        
    def get_next_child(self, request):
        
        """Given a request, calculate the next immediate leaf in the tree.
        
        @param request The HttpRequest object.
        
        @return a leaf object.
        """
        
        if self.next_child is not None:
            return self.next_child
        
        for child in self.children:
            if self.matches(request, child.value):
                self.next_child = child
                return self.next_child
        
        return None
    
    def vacuum(self, request, form):
        """ If this child has not been submitted in the form, remove it.
        Otherwise, vacuum the children.
        
        :param request: The HttpRequest object.
        
        :param form: The django.forms.Form object from which we get the
            fields.
            
        """
        
        logger.debug("Vacuuming %s and its children."%(self.field_name))
        
        if self.children is None or len(self.children) == 0:
            return
        
        for child in self.children:
            if not self.matches(request, child.value):
                form.delete_field(child.field_name)
            child.vacuum(request, form)
        
        
class FieldTree:
    
    def __init__(self, request, form, root, javascript=True):
        """A tree structure containing fields.
        
        @param request The HttpResponse object from the form submit.
        
        @param root The root element. Must be a FieldLeaf.
        
        @param javascript (Optional) True if javascript is active in the web
            browser, False otherwise.
        
        """
        
        self.request = request
        self.form = form
        self.root = root
        
        
    def vacuum(self):
        """ Starting at the root node, delete all the fields that should
        not be shown.
        """
        self.root.vacuum(self.request, self.form)