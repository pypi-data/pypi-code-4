#!/usr/bin/env python3
"""
Module SPECS -- GUI Specification Helper Module
Sub-Package GUI of Package PLIB3 -- Python GUI Framework
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains helper variables and functions for
defining GUI specifications that can be used by the PLIB3
"auto" GUI classes. For an example of usage, see the
pyidserver-gui.py example program.
"""

from plib.gui import main as gui
from plib.gui.common import actiondict, AUTO_TARGET

# Control variables for widget geometries; if you want to
# change these values, you can import specs and mutate them
# as long as you do it before any widgets are constructed

framemargin = 10
tabmargin = 10
panelmargin = 4
panelspacing = 10
buttonwidth = 110
combowidth = 90
editwidth = 210
numeditwidth = 80
labelwidth = 150
listwidth = 250
mainwidth = 400
mainheight = 250

# Classes to be used for each basic widget type; these can also be
# changed to point to custom classes as long as it's done before
# widget creation; note that any such changes will be *global*
# (i.e., they affect all modules using this one in your application),
# so if you just want custom widgets for a particular GUI window or
# dialog, it's better to build their specs by hand (see the _dialogs
# module for an example of how this can be done, with PPrefsDialog)

# These are functions so that the loading of the actual widget modules
# gets deferred until the specs are realized (instead of happening
# when this module is imported), since plib.gui.main itself does not
# load widget classes until the module attributes are accessed

button_class = lambda: gui.PButton
checkbox_class = lambda: gui.PCheckBox
combo_class = lambda: gui.PComboBox
sorted_combo_class = lambda: gui.PSortedComboBox
edit_class = lambda: gui.PEditBox
label_class = lambda: gui.PTextLabel
listbox_class = lambda: gui.PListBox
sorted_listbox_class = lambda: gui.PSortedListBox
listview_class = lambda: gui.PListView
sorted_listview_class = lambda: gui.PSortedListView
memo_class = lambda: gui.PEditControl
table_class = lambda: gui.PTable
text_class = lambda: gui.PTextDisplay

groupbox_class = lambda: gui.PAutoGroupBox
tabwidget_class = lambda: gui.PAutoTabWidget

# Note that we don't need to define a panel class here because any class
# derived from PAutoPanel will automatically use itself to instantiate
# sub-panels; thus all the panel specs here are just lists of sub-widget
# specs for use by whatever panel class you choose.

# These are functions rather than static tuples so that the values
# get pulled dynamically from the above variables

button_geometry = lambda: (None, None, buttonwidth, None)
combo_geometry = lambda: (None, None, combowidth, None)
editgeometry = lambda: (None, None, editwidth, None)
numeditgeometry = lambda: (None, None, numeditwidth, None)
listboxgeometry = lambda: (None, None, listwidth, None)
labelgeometry = lambda: (None, None, labelwidth, None)
main_geometry = lambda: (None, None, mainwidth, mainheight)

# Convenience class to provide header labels with the appropriate
# attributes for the table/list widget APIs; we don't bother deferring
# the loading of the class here since it's just a small one

header_class = gui.PHeaderLabel


# Convenience function for enabling auto-target functionality

def _adjust_target(target, fstr, name):
    # Note that "no target" is None, which isn't touched here
    if target in ('', AUTO_TARGET):
        newtarget = fstr.format(name)
        if target == '':
            return newtarget
        return (target, newtarget)
    return target


# Convenience functions for building specs


def get_padding(name):
    return ([], (), {}, 'padding_{}'.format(name))


def _label_geometry(width):
    if width:
        return (None, None, width, None)
    return labelgeometry()


def get_label(label, name, width=None):
    return (
        label_class,
        ("{}: ".format(label),),
        {'geometry': _label_geometry(width)},
        'label_{}'.format(name)
    )


def get_textlabel(label, name, width=None):
    return (
        label_class,
        (label,),
        {'geometry': _label_geometry(width)},
        'label_{}'.format(name)
    )


def get_checkbox(label, name, target=None):
    return (
        checkbox_class,
        (label,),
        {'target': _adjust_target(target, '{}_toggled', name)},
        'checkbox_{}'.format(name)
    )


def get_combobox(items, name, target=None):
    return (
        combo_class,
        (items,),
        {'target': _adjust_target(target, '{}_selected', name),
            'geometry': combo_geometry()},
        'combo_{}'.format(name)
    )


def get_sorted_combobox(items, name, target=None, key=None):
    return (
        sorted_combo_class,
        (items,),
        {'target': _adjust_target(target, '{}_selected', name),
            'geometry': combo_geometry(), 'key': key},
        'combo_{}'.format(name)
    )


def get_editbox(name, target=None, expand=True):
    return (
        edit_class,
        (),
        {'target': _adjust_target(target, '{}_changed', name),
            'geometry': editgeometry(), 'expand': expand},
        'edit_{}'.format(name)
    )


def get_numeditbox(name, target=None, expand=True):
    return (
        edit_class,
        (),
        {'target': _adjust_target(target, '{}_changed', name),
            'geometry': numeditgeometry(), 'expand': expand},
        'edit_{}'.format(name)
    )


def get_listbox(labels, name, target=None):
    # FIXME: this doesn't appear to properly handle labels with width = -1
    return (
        listbox_class,
        ([header_class(*args) for args in labels],),
        {'target': _adjust_target(target, '{}_selected', name),
            'geometry': listboxgeometry()},
        'listbox_{}'.format(name)
    )


def get_sorted_listbox(labels, name, target=None, key=None):
    # FIXME: this doesn't appear to properly handle labels with width = -1
    return (
        sorted_listbox_class,
        ([header_class(*args) for args in labels],),
        {'target': _adjust_target(target, '{}_selected', name),
            'geometry': listboxgeometry(), 'key': key},
        'listbox_{}'.format(name)
    )


def get_textcontrol(name, text="", scrolling=True):
    return (
        text_class,
        (text,),
        {'geometry': main_geometry(), 'scrolling': scrolling},
        'text_{}'.format(name)
    )


def get_textdisplay(name, text="", scrolling=True):
    return (
        text_class,
        (text,),
        {'scrolling': scrolling},
        'text_{}'.format(name)
    )


def get_editcontrol(name, target=None, scrolling=True):
    return (
        memo_class,
        (),
        {'target': _adjust_target(target, '{}_changed', name),
            'geometry': main_geometry(), 'scrolling': scrolling},
        'memo_{}'.format(name)
    )


def get_memo(name, target=None, scrolling=True):
    return (
        memo_class,
        (),
        {'target': _adjust_target(target, '{}_changed', name),
            'scrolling': scrolling},
        'memo_{}'.format(name)
    )


def get_listview(labels, name, target=None):
    # FIXME: this doesn't appear to properly handle labels with width = -1
    return (
        listview_class,
        ([header_class(*args) for args in labels],),
        {'target': _adjust_target(target, '{}_selected', name)},
        'listview_{}'.format(name)
    )


def get_sorted_listview(labels, name, target=None, key=None):
    # FIXME: this doesn't appear to properly handle labels with width = -1
    return (
        sorted_listview_class,
        ([header_class(*args) for args in labels],),
        {'target': _adjust_target(target, '{}_selected', name), 'key': key},
        'listview_{}'.format(name)
    )


def get_table(labels, name, target=None):
    return (
        table_class,
        ([header_class(*args) for args in labels],),
        {'target': _adjust_target(target, '{}_changed', name)},
        'table_{}'.format(name)
    )


def get_button(caption, name, pxname=None, target=''):
    return (
        button_class,
        (caption, pxname),
        {'target': _adjust_target(target, '{}', name),
            'geometry': button_geometry()},
        'button_{}'.format(name)
    )


def get_action_button(action, name=None, target=''):
    # TODO: do we need more sophisticated error handling here?
    if name is None:
        try:
            name = actiondict[action][0]
        except KeyError:
            name = "Unknown"
    if target == '':
        if name != "Unknown":
            target = name
        else:
            target = None
    return (
        button_class,
        (action, ""),
        {'target': _adjust_target(target, '{}', name),
            'geometry': button_geometry()},
        'button_{}'.format(name)
    )


def get_interior_panel(contents, align, layout, name):
    return (
        contents,
        (),
        {'align': align, 'layout': layout},
        'panel_{}'.format(name)
    )


def get_midlevel_panel(contents, align, layout, name):
    return (
        contents,
        (),
        {'align': align, 'layout': layout,
            'spacing': panelspacing},
        'panel_{}'.format(name)
    )


def get_groupbox(contents, caption, name):
    return (
        groupbox_class,
        (caption, contents),
        {'margin': tabmargin, 'spacing': panelspacing},
        'groupbox_{}'.format(name)
    )


def get_tab_panel(contents, align, layout, name):
    return (
        contents,
        (),
        {'align': align, 'layout': layout,
            'margin': tabmargin, 'spacing': panelspacing},
        'panel_{}'.format(name)
    )


def get_tabwidget(tabs, name, target=None):
    return (
        tabwidget_class,
        (tabs,),
        {'target': _adjust_target(target, '{}_changed', name)},
        'tabs_{}'.format(name)
    )


def get_toplevel_panel(contents, align, layout, name):
    return (
        contents,
        (),
        {'align': align, 'layout': layout,
            'margin': panelmargin, 'spacing': panelspacing},
        'panel_{}'.format(name)
    )


### Alternate API (this will become the norm in version 0.8)

def toplevel_panel(align, layout, name, contents):
    return get_toplevel_panel(contents, align, layout, name)


def groupbox(caption, name, contents):
    return get_groupbox(contents, caption, name)


def tabwidget(name, tabs, target=None):
    return get_tabwidget(tabs, name, target)


def midlevel_panel(align, layout, name, contents):
    return get_midlevel_panel(contents, align, layout, name)


def tab_panel(align, layout, name, contents):
    return get_tab_panel(contents, align, layout, name)


def interior_panel(align, layout, name, contents):
    return get_interior_panel(contents, align, layout, name)


# New API methods, use "auto-targeting" by default

def checkbox(label, name, target=AUTO_TARGET):
    return get_checkbox(label, name, target)


def combobox(name, items, target=AUTO_TARGET):
    return get_combobox(items, name, target)


def sorted_combobox(name, items, target=AUTO_TARGET, key=None):
    return get_sorted_combobox(items, name, target, key)


def editbox(name, target=AUTO_TARGET, expand=True):
    return get_editbox(name, target, expand)


def editcontrol(name, target=AUTO_TARGET, scrolling=True):
    return get_editcontrol(name, target, scrolling)


def listbox(name, labels, target=AUTO_TARGET):
    return get_listbox(labels, name, target)


def sorted_listbox(name, labels, target=AUTO_TARGET, key=None):
    return get_sorted_listbox(labels, name, target, key)


def listview(name, labels, target=AUTO_TARGET):
    return get_listview(labels, name, target)


def sorted_listview(name, labels, target=AUTO_TARGET, key=None):
    return get_sorted_listview(labels, name, target, key)


def table(name, labels, target=AUTO_TARGET):
    return get_table(labels, name, target)


def memo(name, target=AUTO_TARGET, scrolling=True):
    return get_memo(name, target, scrolling)


def numeditbox(name, target=AUTO_TARGET, expand=True):
    return get_numeditbox(name, target, expand)


# New API methods for controls that don't need or don't
# use auto-targeting (the latter are the buttons, which
# should always complain if they don't find event handlers
# since that's the only point of having them)

action_button = get_action_button
button = get_button
label = get_label
padding = get_padding
textcontrol = get_textcontrol
textdisplay = get_textdisplay
textlabel = get_textlabel
