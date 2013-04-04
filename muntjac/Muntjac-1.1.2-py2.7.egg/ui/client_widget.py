# Copyright (C) 2012 Vaadin Ltd. 
# Copyright (C) 2012 Richard Lincoln
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.


class ClientWidget(object):
    """Annotation defining the default client side counterpart in GWT
    terminal for L{Component}.

    With this annotation server side Muntjac component is marked to have
    a client side counterpart. The value of the annotation is the class
    of client side implementation.

    Note, even though client side implementation is needed during
    development, one may safely remove them from the classpath of the
    production server.
    """

    def __init__(self, widget, loadStyle=None):

        #: the client side counterpart for the annotated component
        self.widget = widget

        # Depending on the used WidgetMap generator, these optional hints
        # may be used to define how the client side components are loaded
        # by the browser. The default is to eagerly load all widgets
        # L{EagerWidgetMapGenerator}, but if the
        # L{WidgetMapGenerator} is used by the widgetset, these load
        # style hints are respected.
        #
        # Lazy loading of a widget implementation means the client side
        # component is not included in the initial JavaScript application
        # loaded when the application starts. Instead the implementation
        # is loaded to the client when it is first needed. Lazy loaded
        # widget can be achieved by giving L{LoadStyle#LAZY} value
        # in ClientWidget annotation.
        #
        # Lazy loaded widgets don't stress the size and startup time of
        # the client side as much as eagerly loaded widgets. On the other
        # hand there is a slight latency when lazy loaded widgets are first
        # used as the client side needs to visit the server to fetch the
        # client side implementation.
        #
        # The L{LoadStyle#DEFERRED} will also not stress the initially
        # loaded JavaScript file. If this load style is defined, the widget
        # implementation is preemptively loaded to the browser after the
        # application is started and the communication to server idles.
        # This load style kind of combines the best of both worlds.
        #
        # Fine tunings to widget loading can also be made by overriding
        # L{WidgetMapGenerator} in the GWT module. Tunings might be
        # helpful if the end users have slow connections and especially if
        # they have high latency in their network. The
        # L{CustomWidgetMapGenerator} is an abstract generator
        # implementation for easy customization. Muntjac package also
        # includes L{LazyWidgetMapGenerator} that makes as many
        # widgets lazily loaded as possible.

        #: the hint for the widget set generator how the client side
        #  implementation should be loaded to the browser
        if loadStyle is None:
            self.loadStyle = LoadStyle.DEFERRED
        else:
            self.loadStyle = loadStyle


class LoadStyle(object):
    #: The widget is included in the initial JS sent to the client.
    EAGER = 'EAGER'

    #: Not included in the initial set of widgets, but added to queue from
    #  which it will be loaded when network is not busy or the
    #  implementation is required.
    DEFERRED = 'DEFERRED'

    #: Loaded to the client only if needed.
    LAZY = 'LAZY'
