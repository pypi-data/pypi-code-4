# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute


class IDisplayView(Interface):
    """The view of an object. More explicitly, it defines
    a view that displays an object in a non-editable way.
    """


class ISkin(Interface):
    """API - Skin components.
    """
    IBaseLayer = Attribute("Layer used to register all the "
                           "Dolmen centric view components.")

    IBaseSkin = Attribute("Skin providing the IBaseLayer. Can"
                          " be applied directly or inherited.")

    Resource = Attribute("Viewlet component used to include resources")


class IContentProviders(Interface):
    """API - Registered content providers.
    """
    Header = Attribute("Viewlet manager involved in rendering the HTML head.")
    Top = Attribute("Viewlet manager for the top part of the body.")
    Footer = Attribute("Viewlet manager for the bottom part of the body.")
    AboveBody = Attribute("Viewlet manager located above the main content.")
    BelowBody = Attribute("Viewlet manager located below the main content.")
    Resources = Attribute("Viewlet manager including resources.")


class IGlobalUI(IContentProviders):
    """API - Global user interface components.
    """
    Master = Attribute(
        "Base layout using all the `IContentProviders` components "
        "to build a coherent yet overridable rendering.")


class IContextualUI(Interface):
    """API - Pluggable contextual content.
    """
    FlashMessages = Attribute("Viewlet displaying site-wide messages.")
    ContextualActions = Attribute("Viewlet rendering contextual actions.")


class IModels(Interface):
    """API - Available base classes.
    """
    Page = Attribute("Page embedded in a layout.")
    Index = Attribute("Page showing as default view on an object.")
    Form = Attribute("Generic page form.")


class IBaseViews(Interface):
    """API - Registered view components.
    """
    Add = Attribute("Default add form.")
    Edit = Attribute("Default edit form.")
    Delete = Attribute("Default delete form.")
    DefaultView = Attribute("Display form used as index.")


class IMenus(Interface):
    """API - Public menu components.
    """
    ContextualMenu = Attribute("Menu defining contextual actions.")
    MenuViewlet = Attribute("Generic viewlet rendering a `IBrowserMenu`.")


class IDolmenLayoutAPI(IContentProviders, IGlobalUI, IContextualUI,
                       ISkin, IModels, IBaseViews, IMenus):
    """Dolmen Layout Module API
    """
