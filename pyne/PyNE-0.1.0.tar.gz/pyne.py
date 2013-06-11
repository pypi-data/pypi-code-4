# Copyright (c) 2013 Jordan Halterman <jordan.halterman@gmail.com>
# See LICENSE for details.
"""
Process Networks
================
Process networks are at the core of PyNE. The :py:class:`~pyne.Network`
class handles mapping relationships between network components, creating and
managing communication channels, and starting and stopping component processes.

Network Expressions
-------------------
PyNE network definitions are created using a unique syntax that takes advantage
of Python's "magic" features. This syntax reduces code and creates a clear and
easy to understand outline of network workflows. Network definitions can be created
using any component type. Instead of manually mapping components
via method calls, the user simply defines mappings via an expression. The Network
class parses the network expression and creates mappings internally. The
expression syntax provides readability and ensures that the network map is
stable and reliable. *Expressions are passed as the sole argument to
:py:class:`~pyne.Network` where the physical component connections
are made.*

Network Expression Language (NEL)
+++++++++++++++++++++++++++++++++
The ``>>`` symbol is used to denote a direct connection between the left
element and the right element, with the message flow moving from left to right.
Using ``>>`` we can define a simple pipeline workflow.

.. code-block:: python

   network = (a >> b >> c >> d)

The ``&`` symbol is used to denote a split in the message flow, with a copy
of the left element's message going to each element within the ``&`` expression.

.. code-block:: python

   network = (a >> b >> ((c >> d) & (e >> f)) >> g)

Note that in this network, ``b`` will send its results to both ``c`` and ``e``,
each of which will execute their own pipelines internally. At the end of those
pipelines, ``d`` and ``f`` will each send their results to ``g``. Thus, this network
essentially splits and re-joins.

The ``|`` symbol behaves in the same way as ``&`` except that it is an *or*
expression.

.. code-block:: python

   network = (a >> b >> ((c >> d) | (e >> f)) >> g)

When an element forwards results to two elements bound by an *or*, the message
is placed in a single queue. Each of the target elements will compete for the
message, meaning whichever element gets to the message first will receive it.

A complex network
+++++++++++++++++
Any type of network can be developed with PyNE. This network creates the
following connections between components.

``a - b or c`` ``a - d or e`` ``b - f`` ``c - f`` ``d - f`` ``e - f`` ``f - g``
``f - h`` ``h - i`` ``i - j or k``

.. code-block:: python

   network = (a >> ((b | c) & (d | e)) >> f >> (g & h >> i >> (j | k)))

Components
==========
PyNE components are the workers of PyNE. Each component represents a
child process that executes a callback when the process receives new
messages. Each component within a network should have a *unique address*.

Defining Components
-------------------
PyNE relies on wrapped component callbacks to map processes to each other
and provides a few decorators for defining network component callbacks.
Internally, each component has an ``address`` attribute that must be unique
to the network. Note that if no address is strictly defined within the
component definition, the component callback name will be used.

The required behavior of a component callback depends on where the component
is used within the network. If the component serves as the initial network
process, the component will not receive any messages and thus the callback
must not accept any arguments. Alternatively, if the component serves as
a final network endpoint, any return value from the component will be ignored.
All other components are considered *data processors* and should both accept
a ``data`` argument and return a value or generator.

.. code-block:: python

   from pyne import component

   # A data source process.
   @component
   def do_consume():
     yield 'foo'
     yield 'bar'
     yield 'baz'

   # A data processor.
   @component
   def do_process(data):
     data += 1
     return data

   # A data destination.
   @component
   def do_produce(data):
     print data
"""
from multiprocessing import Process, Queue, Event
from types import GeneratorType
import uuid, time

class Network(object):
  """
  A PyNE process network.

  The process :py:class:`Network` class manages starting network processes and
  maintains communication between network components. The behavior of the network
  can vary depending upon component processes.

  *mappings* is either a PyNE network expression or a list of two-tuples
  containing source and target component mappings. If a network expression
  is passed, the network connections will be automatically created. If
  a list of connection tuples is passed, the connections will be added
  by calling the :py:meth:`~pyne.Network.connect` method.

  Using a network expression

  .. code-block:: python

     from pyne import Network, component

     @component
     def a():
       for i in range(10000):
         yield "%s"%(i,)

     @component
     def b(data):
       for i in range(len(data)):
         yield i

     @component
     def c(data):
       print data

     network = Network(a >> b >> c)
     network.start()

  Using a list of component mappings

  .. code-block:: python

     from pyne import Network, Component

     components = [
       Component(lambda x: x*2),
       Component(lambda x: x-2),
       Component(lambda x: x+2),
     ]
     network = Network([
       (components[0], components[1]),
       (components[1], components[2]),
     ])
     network.start()
  """
  def __init__(self, mappings=None):
    """
    Sets up the network.
    """
    self.connections = []
    if mappings is not None:
      if isinstance(mappings, (list, tuple)):
        for mapping in mappings:
          self.connect(mapping[0], mapping[1])
      else:
        self.connections = self.__create_connections(mappings)

  def __len__(self):
    return len(self.connections)

  def connect(self, source, target):
    """
    Connects two components.

    This is the manual method of connecting two components. It is an
    alternative to the use of PyNE's Network Expression Language syntax.

    If either the *source* or *target* component has already been connected
    to another component, the existing component connection will be used
    and new *input* or *output* channels will be added to that connection.
    If either does not have an existing connection instance, a new connection
    will be created.

    Note that due to massaging symantics, the :py:meth:`~pyne.Network.connect`
    method does not support competing consumer connections as the expression
    language does. Also, components connected via this method should be
    instances of :py:class:`pyne.Component` rather than decorated instances.

    .. code-block:: python

       from pyne import Network

       network = Network()
       comp1, comp2 = Component(lambda: i for i in range(10000)), Component(lambda x: x*2)
       network.connect(comp1, comp2)
    """
    channel = Channel(Queue())
    exists = [False, False]
    for connection in self.connections:
      if connection.component == source:
        connection.add_output_channel(channel)
        exists[0] = True
      elif connection.component == target:
        connection.add_input_channel(channel)
        exists[1] = True

    if not exists[0]:
      connection = Connection(source)
      connection.add_output_channel(channel)
      self.connections.append(connection)
    if not exists[1]:
      connection = Connection(target)
      connection.add_input_channel(channel)
      self.connections.append(connection)

  def __create_connections(self, context, mappings=None):
    """
    Creates a list of connections between network processes.
    """
    if mappings is None:
      mappings = []

    def create_connections(mappings):
      """
      Creates actual component connection instances.
      """
      # connections is a dictionary, keyed by component addresses, with each
      # value containing a three-tuple of component, input and output channels.
      connections = {}
      for source, target in mappings:
        try:
          connections[source.address]
        except KeyError:
          connections[source.address] = Connection(source.component)

        # If the target is a list then target components should compete for
        # messages on the same queue.
        if isinstance(target, list):
          connections[source.address].add_output_channel(Channel(Queue()))
          for t in target:
            try:
              connections[t.address]
            except KeyError:
              connections[t.address] = Connection(t.component)
            connections[t.address].add_input_channel(connections[source.address].output_channels[-1])
        else:
          try:
            connections[target.address]
          except KeyError:
            connections[target.address] = Connection(target.component)
          channel = Channel(Queue())
          connections[source.address].add_output_channel(channel)
          connections[target.address].add_input_channel(channel)
      return connections.values()

    def source_mappings(source, context, mappings):
      """
      Creates mappings from a single source to a multiple destination.
      """
      if isinstance(context, Pipeline):
        mappings.append((source, context[0]))
        self.__create_connections(context, mappings)
      elif isinstance(context, (And, Or)):
        mappings.append((source, context[0]))
        self.__create_connections(context, mappings)
      else:
        mappings.append((source, context))
      return mappings

    def dest_mappings(destination, context, mappings):
      """
      Creates mappings from a multiple destination to a single source.
      """
      if isinstance(context, Pipeline):
        mappings.append((context[-1], destination))
      elif isinstance(context, (And, Or)):
        mappings.append((context[-1], destination))
      else:
        mappings.append((context, destination))
      return mappings

    def dest_and(destination, context):
      """
      Handles '(a & b) >> c' type mappings.
      """
      options = []
      for i in range(len(context)):
        if isinstance(context[i], Pipeline):
          options.append(context[i][-1])
        elif isinstance(context[i], And):
          dest_and(destination, context[i])
        elif isinstance(context[i], Or):
          dest_or(destination, context[i])
        else:
          options.append(context[i])
      for option in options:
        mappings.append((option, destination))
      return options

    def dest_or(destination, context):
      """
      Handles '(a | b) >> c' type mappings.
      """
      options = []
      for i in range(len(context)):
        if isinstance(context[i], Pipeline):
          options.append(context[i][-1])
        elif isinstance(context[i], And):
          dest_and(destination, context[i])
        elif isinstance(context[i], Or):
          dest_or(destination, context[i])
        else:
          options.append(context[i])
      for option in options:
        mappings.append((option, destination))
      return options

    def source_and(source, context):
      """
      Handles 'a >> (b & c)' type mappings.
      """
      options = []
      for i in range(len(context)):
        if isinstance(context[i], Pipeline):
          options.append(context[i][0])
          self.__create_connections(context[i], mappings)
        elif isinstance(context[i], And):
          source_and(source, context[i])
        elif isinstance(context[i], Or):
          source_or(source, context[i])
        else:
          options.append(context[i])
      for option in options:
        mappings.append((source, option))
      return options

    def source_or(source, context):
      """
      Handles 'a >> (b | c)' type mappings.
      """
      options = []
      for i in range(len(context)):
        if isinstance(context[i], Pipeline):
          options.append(context[i][0])
          self.__create_connections(context[i], mappings)
        elif isinstance(context[i], And):
          source_and(source, context[i])
        elif isinstance(context[i], Or):
          source_or(source, context[i])
        else:
          options.append(context[i])
      mappings.append((source, options))
      return options

    for i in range(len(context)):
      current_item = context[i]
      try:
        next_item = context[i+1]
      except IndexError:
        break

      if isinstance(current_item, Pipeline):
        # Pipeline -> Pipeline
        if isinstance(next_item, Pipeline):
          mappings.append((current_item[-1], next_item[0]))
        # Pipeline -> And
        elif isinstance(next_item, And):
          source_and(current_item[-1], next_item)
        # Pipeline -> Or
        elif isinstance(next_item, Or):
          source_or((current_item[-1], next_item))
        # Pipeline -> Processor
        else:
          dest_mappings(next_item, current_item, mappings)
      elif isinstance(current_item, And):
        if isinstance(next_item, Pipeline):
          dest_and(next_item[0], current_item)
        elif isinstance(next_item, (And, Or)):
          raise NetworkError("Cannot route and/or context to and/or context.")
        else:
          dest_and(next_item, current_item)
      elif isinstance(current_item, Or):
        if isinstance(next_item, Pipeline):
          dest_or(next_item[0], current_item)
        elif isinstance(next_item, (And, Or)):
          raise NetworkError("Cannot route and/or context to and/or context.")
        else:
          dest_or(next_item, current_item)
      else:
        # Processor -> Pipeline
        if isinstance(next_item, Pipeline):
          mappings.append((current_item, next_item[0]))
          self.__create_connections(next_item)
        # Processor -> And
        elif isinstance(next_item, And):
          source_and(current_item, next_item)
        # Processor -> Or
        elif isinstance(next_item, Or):
          source_or(current_item, next_item)
        # Processor -> Processor
        else:
          mappings.append((current_item, next_item))

    return create_connections(mappings)

  def start(self, *args, **kwargs):
    """
    Starts the network.

    *args* and *kwargs* are additional arguments to pass to *all*
    input components. Input components are defined as components whose
    :py:class:`pyne.Connection` contains no input channels and
    one or more output channel.

    Raises a :py:class:`pyne.NetworkError` if the network does not
    contain enough components.
    """
    if len(self.connections) < 2:
      raise NetworkError("Not enough network components.")
    for connection in self.connections:
      connection.component.start(*args, **kwargs)

  def run(self, *args, **kwargs):
    """
    Runs the network, blocking until all processes have completed.

    *args* and *kwargs* are additional arguments to pass to *all*
    input components. Input components are defined as components whose
    :py:class:`pyne.Connection` contains no input channels and
    one or more output channel.

    Raises a :py:class:`pyne.NetworkError` if the network does not
    contain enough components.
    """
    if len(self.connections) < 2:
      raise NetworkError("Not enough network components.")
    for connection in self.connections:
      connection.component.start(*args, **kwargs)
    for connection in self.connections:
      connection.component.join()

class Channel(object):
  """
  A communication channel.

  Channels support direct communication between a two single components.
  Channels reside within a :py:class:`pyne.Connection` instance,
  and are often grouped with a single connection containing either
  multiple input or multiple output channels. Each channel contains a
  shared :py:class:`multiprocessing.Queue` instance for communication
  between components and a :py:class:`multiprocessing.Event` instance
  which is used to indicate the status of the channel. Once a component
  has completed processing all input data from all input channels, it
  will automatically set the *status* flag.

  *queue* is an instance that exposes the :py:class:`Queue.Queue` interface.

  *status* is a :py:class:`multiprocessing.Event` instance representing
  the current channel status.
  """
  def __init__(self, queue):
    self.queue = queue
    self.status = Event()
    self.open()

  def open(self):
    """
    Sets the channel status flag.
    """
    self.status.set()

  def close(self):
    """
    Clears the channel status flag.
    """
    self.status.clear()

  def is_open(self):
    """
    Indicates whether the channel status flag is currently set.
    """
    return self.status.is_set()

  def put(self, data, *args, **kwargs):
    """
    Puts a message in the channel.

    *data* is the data to send.
    """
    self.open()
    self.queue.put(data, *args, **kwargs)

  def get(self, *args, **kwargs):
    """
    Gets a message from the channel.
    """
    return self.queue.get(*args, **kwargs)

  def empty(self):
    """
    Indicates whether the channel is empty.
    """
    return self.queue.empty()

class Connection(object):
  """
  A network component connection.

  The component connection represents a network process's input and output
  channels and thus its relationship with related processes. Each network
  component will always belong to exactly *one* connection. Connections
  are essentially used an abstraction to support complex relationships
  between disparate components.

  *component* is the network component object.

  *input_channels* is a list of component input channels. (Default: None)

  *output_channels* is a list of component output channels. (Default: None)
  """
  def __init__(self, component, input_channels=None, output_channels=None):
    self.component = component
    self.component.connection = self
    self.input_channels = input_channels or []
    self.output_channels = output_channels or []
    self.__receive = None

  def add_input_channel(self, channel):
    """
    Adds an input channel to the connection.
    """
    self.input_channels.append(channel)
    return self

  def add_output_channel(self, channel):
    """
    Adds an output channel to the connection.
    """
    self.output_channels.append(channel)
    return self

  def open(self):
    """
    Opens output channels.

    This method is called when a component first begins receiving data.
    It prepares following components for receiving data by indicating
    that all of the component's output channels are open for receiving
    messages.
    """
    for channel in self.output_channels:
      channel.open()

  def close(self):
    """
    Closes output channels.

    This method is called when a component has completed all data
    processing. It will set *all* output channel flags, indicating to
    the components to which they are connected that this component has
    completed data processing.
    """
    for channel in self.output_channels:
      channel.close()

  def can_send(self):
    """
    Returns a boolean indicating whether the connection has output channels.

    This can be used to determine a component's intended behavior based
    on the network configuration.
    """
    return len(self.output_channels) > 0

  def send(self, data, block=True, timeout=None):
    """
    Sends data to the connection.

    This method sends a copy of *data* to each output channel contained
    within the connection.

    *data* is the data to send.

    *block* indicates whether to block if the channel is full.

    *timeout* is an optional timeout when in blocking mode.
    """
    for channel in self.output_channels:
      channel.put(data, block, timeout)

  def can_receive(self):
    """
    Returns a boolean indicating whether the connection has input channels.

    This can be used to determine a component's intended behavior based
    on the network configuration.
    """
    return len(self.input_channels) > 0

  def receive(self, block=True, timeout=None):
    """
    Receives data from the connection.

    This method attempts to receive data from each input channel contained
    within the connection. If all input channels have been closed by
    their respective source components, a :py:class:`pyne.ConnectionError`
    will be raised, indicating that the component will not receive any
    further messages. This notification should be used to close output
    channels once data processing is complete.

    *block* indicates whether to block if the channel is full.

    *timeout* is an optional timeout when in blocking mode.
    """
    def do_receive():
      input_count = len(self.input_channels)
      while True:
        closed_count = 0
        for channel in self.input_channels:
          try:
            data = channel.get(False)
          except:
            if not channel.is_open():
              closed_count += 1
          else:
            if data is not None:
              yield data
        if closed_count == input_count:
          raise ConnectionError("Input channels are closed.")

    if block is True:
      if self.__receive is None:
        self.__receive = do_receive()
      while True:
        try:
          data = self.__receive.next()
          if data is not None:
            return data
        except StopIteration:
          is_open = False
          for channel in self.input_channels:
            if channel.is_open():
              is_open = True
          if is_open is True:
            self.__receive = do_receive()
            continue
          else:
            raise ConnectionError("Input channels are closed.")
    else:
      if self.__receive is None:
        self.__receive = do_receive()
      try:
        return self.__receive.next()
      except StopIteration:
        raise ConnectionError("Input channels are closed.")

class Component(object):
  """
  A network component.

  For use of component instances in PyNE network expressions, components
  *must* be decorated with the :py:class:`~pyne.component` decorator.
  This decorator contains the methods required for PyNE syntax.

  .. code-block:: python

     from pyne import component
     @component
     def foo(data):
       for i in range(len(data)):
         yield i

  *callback* is a callable object. The callback should accept a single
  argument and return either a value or a generator. If a generator
  is returned by the callback, each generator value will be sent through
  the component's output channel as a single message.
  """
  def __init__(self, callback):
    self.callback, self.address = callback, uuid.uuid4()
    self.process, self.connection = None, None

  def __getattr__(self, name):
    """
    Supports accessing the internal component process attributes.
    """
    return getattr(self.process, name)

  def start(self, *args, **kwargs):
    """
    Starts the component process.

    *args* and *kwargs* are additional arguments to be passed to the
    component callback *if this is an input component.* If the component
    is not an input component then additional arguments will be ignored.
    """
    if self.connection is None:
      raise ConnectionError("No component connection.")
    self.process = Process(target=self.run, args=args, kwargs=kwargs)
    self.process.start()
    return self.process

  def run(self, *args, **kwargs):
    """
    Runs the component process.

    *args* and *kwargs* are additional arguments to be passed to the
    component callback *if this is an input component.* If the component
    is not an input component then additional arguments will be ignored.
    """
    if self.connection is None:
      raise ConnectionError("No component connection.")

    def run_input(connection, *args, **kwargs):
      """Runs the component as an input process."""
      connection.open()
      results = self(*args, **kwargs)
      if isinstance(results, GeneratorType):
        for result in results:
          connection.send(result)
      else:
        connection.send(results)
      connection.close()

    def run_processor(connection):
      """Runs the component as a data processor."""
      connection.open()
      try:
        while True:
          data = connection.receive(False)
          while data is not None:
            results = self(data)
            if results is not None:
              if isinstance(results, GeneratorType):
                for result in results:
                  connection.send(result)
              else:
                connection.send(results)
            data = connection.receive()
          time.sleep(.5)
      except ConnectionError:
        connection.close()

    def run_output(connection):
      """Runs the component as an output process."""
      connection.open()
      try:
        while True:
          data = connection.receive()
          while data is not None:
            self(data)
            data = connection.receive()
          if not connection.is_open():
            connection.close()
          time.sleep(.5)
      except ConnectionError:
        connection.close()

    # If this connection can send and receive then this is a data processor.
    # If it can receive but not send, it's an output endpoint.
    # If it can send but not receive, it's an input endpoint.
    # Otherwise, this process needs to be exited.
    if self.connection.can_receive():
      if self.connection.can_send():
        run_processor(self.connection)
      else:
        run_output(self.connection)
    elif self.connection.can_send():
      run_input(self.connection, *args, **kwargs)
    else:
      raise ConnectionError("Invalid component connection.")

  def __call__(self, *args, **kwargs):
    """
    Executes the component callback.
    """
    return self.callback(*args, **kwargs)

  def __repr__(self):
    return '%s(%s)' % (self.__class__.__name__, self.address)

class component(object):
  """
  A component wrapper that supports the PyNE Network Expression Language.

  This wrapper is intended to be used as a decorator. It is *required
  for use with the PyNE Network Expression Language.* The standard
  :py:class:`pyne.Component` class does not contain the "magic methods"
  required for NEL syntax. This function decorates the component with
  the required methods.

  .. code-block:: python

     from pyne import component

     @component
     def a():
       for i in range(10000):
         yield "%s"%(i,)

     @component
     def b(data):
       for i in range(len(data)):
         yield i

     @component
     def c(data):
       print data

     network = a >> b >> c
  """
  def __init__(self, callback):
    self.component = Component(callback)

  def __getattr__(self, name):
    """
    Supports accessing component attributes directly.
    """
    return getattr(self.component, name)

  def __rshift__(self, component):
    """
    Inserts the component into a pipeline.
    """
    return Pipeline(self, component)

  def __and__(self, component):
    """
    Inserts the component into an AND context.
    """
    return And(self, component)

  def __or__(self, component):
    """
    Inserts the processor into an OR context.
    """
    return Or(self, component)

class Element(object):
  """
  A network element.
  """
  def __init__(self, *components):
    self.components = list(components)

  def __len__(self):
    return len(self.components)

  def __iter__(self):
    return iter(self.components)

  def __getitem__(self, index):
    return self.components[index]

  def __setitem__(self, index, value):
    self.components[index] = value

  def __repr__(self):
    return '%s(%s)' % (self.__class__.__name__, self.components)

  def build(self):
    """
    Builds a process network from the network expression.
    """
    return Network(self)

  def start(self, *args, **kwargs):
    """
    Supports starting a process network directly from the network expression.
    """
    return Network(self).start(*args, **kwargs)

  def run(self, *args, **kwargs):
    """
    Supports running a process network directly from the network expression.
    """
    return Network(self).run(*args, **kwargs)

class Pipeline(Element):
  """
  A direct pipeline element.
  """
  def __rshift__(self, component):
    """
    Adds a component to the pipeline.
    """
    self.components.append(component)
    return self

  def __irshift__(self, component):
    """
    Adds the component to the pipeline.
    """
    self.components.append(component)
    return self

  def __and__(self, component):
    """
    Adds the pipeline to an AND element.
    """
    return And(self, component)

  def __iand__(self, component):
    """
    Adds the pipeline to an AND element.
    """
    return And(self, component)

  def __or__(self, component):
    """
    Adds the pipeline to an OR element.
    """
    return Or(self, component)

  def __ior__(self, component):
    """
    Adds the pipeline to an OR element.
    """
    return Or(self, component)

class And(Element):
  """
  An AND splitter element.
  """
  def __rshift__(self, component):
    """
    Adds the context to a pipeline.
    """
    return Pipeline(self, component)

  def __irshift__(self, component):
    """
    Adds the context to a pipeline.
    """
    return Pipeline(self, component)

  def __and__(self, component):
    """
    Adds the context to an AND element.
    """
    self.components.append(component)
    return self

  def __iand__(self, component):
    """
    Adds the context to an AND element.
    """
    self.components.append(component)
    return self

  def __or__(self, component):
    """
    Adds the context to an OR element.
    """
    return Or(self, component)

  def __ior__(self, component):
    """
    Adds the context to an OR element.
    """
    return Or(self, component)

class Or(Element):
  """
  An OR splitter element.
  """
  def __rshift__(self, component):
    """
    Adds the context to a pipeline.
    """
    return Pipeline(self, component)

  def __irshift__(self, component):
    """
    Adds the context to a pipeline.
    """
    return Pipeline(self, component)

  def __and__(self, component):
    """
    Adds the context to an AND element.
    """
    return And(self, component)

  def __iand__(self, component):
    """
    Adds the context to an AND element.
    """
    return And(self, component)

  def __or__(self, component):
    """
    Adds the context to an OR element.
    """
    self.components.append(component)
    return self

  def __ior__(self, component):
    """
    Adds the context to an OR element.
    """
    self.components.append(component)
    return self

class PyneError(Exception):
  """
  A base PyNE library error.
  """

class NetworkError(PyneError):
  """
  A process network error.
  """

class ConnectionError(PyneError):
  """
  A component connection error.
  """

all_errors = PyneError
