# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# pyojo                                            Copyright (c) 2011 nabla.net
#------------------------------------------------------------------------------
""" The bootstrap module for the Dojo Toolkit.

The dojo package is the foundation package of the Dojo Toolkit. It consists of 
three main areas:

 - **dojo.js**: This file provides the bootstrap for loading other modules, 
   in particular the require() function.
 - **dojo/_base**: basic functionality historically pulled in as part of 
   dojo.js, and historically existing directly under the dojo namespace
 - **Dojo Core**: more advanced functionality, with some of the functionality 
   available in sub-packages (e.g. dojo/dnd and dojo/store)



Events
------

With Dojo, you connect functions to one another, creating a link that calls one 
function when another fires. You can connect a function of your own to:

 - a **DOM event**, such as when a link is clicked.
 - an **event of an object**, such as an animation starting or stopping
 - a **function** call of your own, such as bar()
 - a **topic**, which acts as a queue that other objects can publish objects to.

Event names now are lower case, Dojo will add “on” to your event name if you 
leave it off. A example::

    dojo.query(".foo").onclick(function(e){
                                            /* handle the event */ 
                    }).onmouseenter(function(e){ 
                                            /* handle event */ });


Available events: onclick, onfocus, onblur, onchange, onkeypress, onkeydown,
onkeyup, onmouseover, onmouseout, onmouseenter, onmouseleave, onmousewheel[-],
onsubmit ...

Event object
++++++++++++

When you connect a function to a DOM event, Dojo passes your function a 
normalized event object containing:


 - *event.target*: the element that generated the event.
 - *event.currentTarget*: the current target.
 - *event.layerX*: the x coordinate, relative to the event.currentTarget.
 - *event.layerY*: the y coordinate, relative to the event.currentTarget.
 - *event.pageX*: the x coordinate, relative to the view port.
 - *event.pageY*: the y coordinate, relative to the view port.
 - *event.relatedTarget*: For onmouseover and onmouseout, the object that the 
   mouse pointer is moving to or out of.
 - *event.charCode*: For keypress events, the character code of the key pressed.
 - *event.keyCode*: for keypress events, handles special keys like ENTER and 
   spacebar.
 - *event.charOrCode*: a normalized version of charCode and keyCode, which can 
   be used for direct comparison for alpha keys and special keys together. 
 - *event.preventDefault()*: - prevent an event’s default behavior.
 - *event.stopPropagation()*: - prevent an event from triggering a parent 
   node’s event.

Additionally, dojo.stopEvent(event) will prevent both default behavior and any 
propagation of an event.


.. note::
   
   dojo.connect can connect to any function, method, or event. Using 
   dijit.byId, we’re passed a reference to the Widget, and are connecting to 
   it’s ‘onClick’ stub. Widget Events in the sense Dijit uses mixedCase event 
   names, to avoid potential conflicts.


Page Load and Unload
++++++++++++++++++++

Dojo has three functions recommended for registering code to run on page load 
and unload:

 - *dojo.ready(func)*: Runs the specified function after the page has finished 
   loading, dojo.require() calls have completed, and the parser (if enabled) 
   has instantiated widgets.
 - *dojo.addOnWindowUnload(func)*: Runs on page unload. Useful for tear-down 
   releasing resources (destroying widgets, etc.), but some browsers limit what 
   operations can be done at this stage, especially DOM access / manipulation.
 - *dojo.addOnUnload(func)*: This also runs on page unload, but earlier than 
    dojo.addOnWindowUnload(func), avoiding the restrictions mentioned above. 
    However, it may be called even when the page isn’t unloading, just because 
    a user clicked a hyperlink to download a file. Useful for idempotent 
    operations like saving state.


Publisher-Subscriber
++++++++++++++++++++

This is dojo’s topic system, to separate components to communicate without 
explicit knowledge of one another’s internals. dojo.publish calls any functions 
that are connected to the topic via dojo.subcribe, passing to those subscribed 
functions arguments that are published.

We can use a function or a method::

    function myFunc(arg){ console.debug("myFunc(" + arg + ") called");}
    var myObj = {
        method: function(a, b){ 
                    console.debug("myObj.method("+a+",  "+b); 
                    return 7; },
                }

And then unsubscribe::

    topics = [];
    topics[0] = dojo.subscribe("topicFunc", myFunc);
    topics[1] = dojo.subscribe("topicMethod2", myObj, "method");

And they will listen to this::

    dojo.publish("topicFunc", ["data from an interesting source"]);
    dojo.publish("topicMethod2", ["Arg1", "Arg2"]);

Later, we can stop listening::

    dojo.unsubscribe(topics[1]);



"""


from _base import *
from _code import *
from _data import *
from _dom import *
from _events import *
from _browser import *
    
