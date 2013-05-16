  # -*- extra stuff goes here -*- 
from wildcard.uberoverride.widgets import ChoiceTreeWidget


def initialize(context):
    from plone.portlet.collection.collection import AddForm, EditForm
    AddForm.form_fields['target_collection'].custom_widget = ChoiceTreeWidget
    EditForm.form_fields['target_collection'].custom_widget = ChoiceTreeWidget

    try:
        from collective.listingviews.browser.portlets.portlets import (
                ListingAddForm,
                ListingEditForm)
        ListingAddForm.form_fields['root'].custom_widget = ChoiceTreeWidget
        ListingEditForm.form_fields['root'].custom_widget = ChoiceTreeWidget
    except ImportError:
        pass

