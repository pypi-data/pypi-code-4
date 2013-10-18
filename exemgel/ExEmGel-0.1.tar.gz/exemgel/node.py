

class Node(object):
    def __init__(self, element):
        self._element = element

    def _make_new_node_or_leaf(self, new_element):
        if len(list(new_element.iter())) == 1 \
                and len(new_element.keys()) == 0:
            text = new_element.text
            if text.isdigit():
                return int(text)
            return text
        else:
            return Node(new_element)

    def __str__(self):
        return self._element.text

    text = property(__str__)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        l = list(self._element.iter(attr))
        if len(l) == 1:
            return self._make_new_node_or_leaf(l[0])
        elif len(l) > 1:
            return tuple([self._make_new_node_or_leaf(e) for e in l])
        if attr in self._element.keys():
            return self._element.get(attr)
        
        raise AttributeError("%r object has no attribute %r" %
                                         (self.__class__, attr))

    
