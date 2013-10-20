from interface import interface

import inspect

#===========================================================

@interface
class IAnnotationRegistry(object):
    def add(self, clazz, ann):
        """Associates annotation with specified class"""

    def getByClass(self, clazz):
        """Returns all associated annotations"""

#===========================================================

class ClassTaggingRegistry(IAnnotationRegistry):
    def add(self, clazz, ann):
        """
        :type clazz: type
        """
        annots = clazz.__dict__.get('__annots__')

        if annots is None:
            annots = []
            setattr(clazz, '__annots__', annots)

        annots.append(ann)

    def getByClass(self, clazz):
        return clazz.__dict__.get('__annots__', [])


#===========================================================

class Annotations(object):
    _registry = ClassTaggingRegistry()

    @staticmethod
    def getAnnotations(clazz):
        return Annotations._registry.getByClass(clazz)

    @staticmethod
    def addAnnotation(clazz, ann):
        Annotations._registry.add(clazz, ann)

    @staticmethod
    def getAnnotatedClasses(module, ann_type):
        def findAnnotations(clazz):
            return [a for a in Annotations._registry.getByClass(clazz) if isinstance(a, ann_type)]

        all_classes = inspect.getmembers(module, inspect.isclass)
        defined_classes = (c for n, c in all_classes if c.__module__ == module.__name__)
        annotated = ((c, findAnnotations(c)) for c in defined_classes)
        return [(c, anns) for c, anns in annotated if anns]

#===========================================================

class ClassAnnotation(object):
    def __init__(self, *va, **ka):
        self.args = (va, ka)

    def __call__(self, t):
        self.apply(t, *self.args[0], **self.args[1])
        Annotations.addAnnotation(t, self)
        return t

    def apply(self, t, *vargs, **kwargs):
        pass
