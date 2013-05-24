from ..models import DocumentCollection

class FeinCMSCollection(DocumentCollection):
    """Extended with support for FeinCMS documents

    Content types in a FeinCMS document will be automatically
    included in the result documents. If you want to include
    any relations of the content types, you need to add them
    explicitly. (TODO: determine the best way to specify these)

    NOTE: This implementation and the signal handlers installed make
    the implicit assumption that content types are only changed if the
    containing document object (Page, or something else inheriting from
    Base) is changed. In normal use where the object is edited through the
    Django Admin, this is always the case.


    """
    # FIXME: we also need to extend get_related_models()!
    # TODO: add special support for MPTT trees?
    # FIXME: extend get_related_models() with content types and
    #        all models underneath them
    # TODO: I'm not too happy with the current special selector
    #       syntax, see if we can do it in cleaner better way
    # TODO: Find out if a change to any of the MPTT fields in a Page
    #       triggers Django's model signals for all updated Pages.
    #       If so, this allows safe inclusion of these fields.

    @staticmethod
    def feincms_regions(obj):
        """Returns as list of valid region names (keys)"""
        templates = obj._feincms_templates
        template = templates[obj.template_key]
        return [ r.key for r in template.regions ]

    def transform_data(self, model, obj, data, path):
        # TODO: At this moment, all the related data should be loaded
        if hasattr(model, '_feincms_content_types'):
            regions = self.feincms_regions(obj)
            content = {}
            for region in regions:
                region_data = []
                for ct in getattr(obj.content, region):
                    # ct is an instantiated content type model
                    ct_model = ct.__class__
                    ct_classname = ct_model.__name__
                    # NOTE: you can use a special selector like
                    # 'content__RichTextContent__text' FIXME: maybe not?
                    ct_data = self.dump_obj(
                        ct_model, ct, path + ['content', ct_classname])
                    ct_data['content_class'] = ct_classname
                    ct_data['content_app_label'] = ct_model._meta.app_label
                    region_data.append(ct_data)
                content[region] = region_data
            data['content'] = content

            # FeinCMS Page cached url:
            # A change in this field will trigger a .save() on all affected
            # pages, so we can safely include this field.
            if hasattr(obj, '_cached_url'):
                data['cached_url'] = obj._cached_url

            # TODO: MPTT tree - not sure we should support it in here, and how
            # FIXME: Make sure these are updated when the tree changes!
            #        Disabled for now, until we find a solution
            #        => Checked: MPTT does raw SQL, so we cannot detect these changes!
            #if hasattr(obj, 'tree_id') and hasattr(obj, 'lft') and hasattr(obj, 'rght'):
                #data['_children'] = list(obj.children.all().values_list('id', flat=True))
                #data['_ancestors'] = list(obj.get_ancestors(
                #    ascending=False, include_self=False).values_list('id', flat=True))
        return super(FeinCMSCollection, self).transform_data(model, obj, data, path)

