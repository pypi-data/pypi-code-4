# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" The pyojo subpackage for Dojo Dijit widgets.

Widgets
-------

All widgets always inherit from dijit._Widget::

    dojo.declare("MyWidget", [dijit._Widget], { ... });

Usually widgets also extend other mixins such as dijit._Templated.

Attributes
----------

Wiggets are placed in the DOM at a:

 - *domNode*: a reference to the overall parent node of the widget itself.
 - *containerNode*: optional parent.

The *attributeMap* specifies a mapping of widget attributes into the DOM tree 
for the widget.

 - **id**: a unique string
 - **lang**: a rarely used string that can override the default Dojo locale
 - **dir**: bi-directional support
 - **class**: HTML class attribute for the widget's domNode
 - **style**: HTML style attribute for the widget's domNode
 - **title**: HTML title attribute for native tooltips
 - **tooltip**: optional dijit.Tooltip reference
 - **baseClass**: root CSS class of the widget
 - **srcNodeRef**: the original DOM node that existed before it was 
   "widgetfied"


Methods
-------

Create custom getter and setter methods; when using your own widgets, use the 
get() and set() methods for field access. In addition, when defining your 
custom setter methods, you should always use the internal _set method, as this 
mechanism allows for the new watch functionality from dojo.Stateful, which all 
widgets now inherit from. 

**get()**

    var value = myWidget.get("foo");
    _getFooAttr: function(){ /* do something */ },

**set()**

    myWidget.set("value", someValue);
    _setValueAttr: function(value){ 
        this.onChange(this.value, value);
        this._set("value", value);},


**onChange()**

    It is designed to work with dojo.connect::
    
        onChange: function(oldValue, newValue){ }

**watch()**

    To detect when attribute values change::

        myTitlePane.watch("open", function(attr, oldVal, newVal){
           console.log("pane is now " + (newVal ? "opened" : "closed"));})



This functions define the lifecycle of a widget:

 - *constructor()*: Called before the parameters are mixed into the widget.
 - *postMixinProperties()*: Invoked before any dom nodes are created.
 - *buildRendering()*: nodes are created, assigned to this.domNode and events 
   hooked up. 
 - *postCreate()*: this is the most important one. The widget has been rendered,
   but sub-widgets in the containerNode have not.
 - *startup()*: Complete parsing and creation of any child widgets. When 
   instantiating a widget programmatically, always call this method.

 - *resize()*: All widgets should have it.
 - *destroy()*: If you have special tear-down work to do.

Assume that you are overriding a method that may do something important:

    postCreate: function() {
      // do my stuff, then...
      this.inherited(arguments);
    }



Events 
------

Can be overriden::

    var myWidget = new dijit.form.Button({
        label: "click me!",
        onClick: myFunc
     });

Or connected using connect() and subscribe()::
    
    //  assume we have a button widget called "btn",
    //  and we want the button to listen to foo.bar():
     
    btn.connect(foo, "bar", function(){
        //  note that "bar" is executed in the scope of btn!
        this.set("something", somethingFromFoo);
    });



 - *mouse-based events*: onClick, onDblClick, onMouseMove, onMouseDown,
   onMouseOut, onMouseOver, onMouseLeave, onMouseEnter, onMouseUp.
 
 - *key-based events*: onKeyDown, onKeyPress, onKeyUp.
 
 - *additional events*: onFocus, onBlur, onShow, onHide, onClose


"""


from base import *
from basic import *

        
