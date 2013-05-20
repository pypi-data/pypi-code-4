# -*- encoding: utf-8 -*-
""" GRouter GObj

.. autoclass:: GRouter
    :members:

"""

"""

GinsFSM forma parte de GObj-Ecosistema, un sistema donde el elemento basico
es un GObj, un objecto cuyo comportamiento esta definido por un automata,
y donde toda la comunicación con el objecto se realiza a traves de eventos.
El GObj define qué eventos de entrada soporta, y que eventos de salida ofrece.
A un GObj puedes enviarle un evento, o subscribirte a sus eventos de salida.

Puedes enviar y subscribir eventos de un GObj que esté en tu mismo thread,
en otros threads o subprocesos de tu aplicación, o en procesos corriendo
en la misma o diferente maquina. Esto incluye también a los browsers.

El transporte de los eventos se realiza mediante el protocolo websocket.
Cada thread o subproceso, representado por el object GAplic,
puede levantar un servicio websocket como
servidor o establecer tantas conexiones cliente como necesite (GRouter)
Se puede configurar un servidor websocket en cualquier puerto.
tambien en el puerto 80 o 443,
en este caso retringido a usar un servidor sockjs integrado
en el framework Pyramid, soportando ademas conexiones de browsers.

Para los GObj corriendo en browsers se usa la libreria sockjs. Esto permite
usar tanto navegadores modernos que soporten websocket, como navegadores
antiguos que no dispongan de websocket.

En el GObj-Ecosistema los threads o suprocesos estan representados por el
objecto GAplic, que además de ser el contenedor de todos los GObj del thread,
y suministrar el event loop, se puede definir con un nombre y uno varios roles.

Puedes configurar una red de gaplics, e intercambiar eventos entre ellos
simplemente conociendo el nombre o role del gaplic, y el nombre del gobj


NEW IDEAS:
Los eventos se garantiza que se entregan al siguiente nodo.
Si se ha podido entregar entonces llega el ack
que provoca que se borre de la cola.
Motivos para que no llege:
    destino desconectado,
    destinatario desconocido en el destino
    cola destinatario llena.

Las tarjetas de presentación son obligatorias si se quiere tener
eventos en sentido contrario, de retorno,
por ejemplo cuando se quiere recibir el return de la acción.

Las tarjetas de presentación no necesitan ack.
En cada conexión automáticamente se enviará la tarjeta de presentación
(solo los clientes: el cliente enviará al servidor conectado su tj.pr.)

Se podría tener un ack de la tr.pr.
que serviría para actualizar, comprobar, ampliar el nombre/roles
que disponemos de ese cliente.
El nombre y roles con que hemos configurado la url de una ruta estática,
no tiene porque coincidir con la que realmente tenga
el dueño de la ruta estática.

Para el sistema de alarmas es importante conocer los nak producidos,
donde se producen y el motivo.
Con esta información se podrán subsanar errores de configuración en el sistema.

Para el sistema de alarmas es importante conocer las desconexiones de las
rutas estáticas.
(CONECTADO/DESCONECTADO)
Con esta información se podrá poner en marcha un sistema de alerta
y comunicación a los afectados, para subsanar lo antes posible el problema.
En este caso, ya no es competencia exclusiva nuestra, sino que pueden
necesitar intervenir agentes externos.

Otro nivel superior de alarmas se puede establecer para informar
de la falta de acuses de recibo a nivel de mensajes de aplicación.
(PROVEEDOR NO CONTESTA)
No sé si se podrá establecer algo genérico para todos.

A nivel de estadísticas, eventos y bytes recibidos y transmitidos por
cada ruta (aparte de los estados de conexión, log activado, etc).

Los eventos podrán tener la propiedad de garantizados:
garantizados por un tiempo: finito o infinito.

Los eventos garantizados se enviarán al role Contenedor de garantizados.
En el Contenedor de garantizados, el estado optimo es todo vacio.
Las alarmas se fijarán en los niveles de llenado del contenedor.
El contenedor se encargará de borrar los eventos caducados e informar al
sistema de alarmas.

El contenedor de garantizados, podrá consultar al registro global de gobjs,
para ver si puede entregar los eventos.

El registro global de gobjs... todos los gaplics deberian registrarse alli.
"""

import datetime
from collections import deque
from ginsfsm.gobj import (
    GObj,
    GObjError,
)
from ginsfsm.c_srv_sock import GServerSock
from ginsfsm.c_connex import GConnex
from ginsfsm.c_timer import GTimer
from ginsfsm.protocols.sockjs.server.c_websocket import GWebSocket
from ginsfsm.protocols.sockjs.server.conn import SockJSConnection
from ginsfsm.protocols.sockjs.server.c_sockjs_server import GSockjsServer
from ginsfsm.utils import (
    get_host_port_from_urls,
    get_path_from_url,
    hexdump,
    random_key,
)
from ginsfsm.protocols.sockjs.server.proto import json_decode


class ExternalSubscription(object):
    """ Container of external subscription.
    """
    def __init__(self, intra_event, route_ref):
        self.event_name = intra_event.event_name
        self.destination_gaplic = intra_event.destination_gaplic
        self.destination_role = intra_event.destination_role
        self.destination_gobj = intra_event.destination_gobj
        self.origin_gaplic = intra_event.origin_gaplic
        self.origin_role = intra_event.origin_role
        self.origin_gobj = intra_event.origin_gobj
        self.route_ref = route_ref
        self.isubscription = None  # reference to internal subscription


class IntraEvent(object):
    """ Container of intra event.
    """
    event_fields = [
        'message_type',
        'serial',
        'event_name',
        'destination_gaplic',
        'destination_role',
        'destination_gobj',
        'origin_gaplic',
        'origin_role',
        'origin_gobj',
        'kw',
    ]
    event_ack_fields = [
        'message_type',
        'serial',
        'event_name',
        'reference',
    ]
    event_nack_fields = [
        'message_type',
        'serial',
        'event_name',
        'error_message',
    ]
    identity_card_fields = [
        'message_type',
        'my_gaplic_name',
        'my_roles',
    ]
    identity_card_ack_fields = [
        'message_type',
        'my_gaplic_name',
        'my_roles',
    ]

    def __init__(
            self,
            message_type=None,
            route_ref=None,
            serial=None,
            event_name=None,
            destination_gaplic=None,
            destination_role=None,
            destination_gobj=None,
            origin_gaplic=None,
            origin_role=None,
            origin_gobj=None,
            my_gaplic_name=None,
            my_roles=None,
            kw=None,
            error_message=None,
            reference=None):
        self.message_type = message_type
        self.route_ref = route_ref
        self.serial = serial
        self.event_name = event_name
        self.destination_gaplic = destination_gaplic
        self.destination_role = destination_role
        self.destination_gobj = destination_gobj
        self.origin_gaplic = origin_gaplic
        self.origin_role = origin_role
        self.origin_gobj = origin_gobj
        self.my_gaplic_name = my_gaplic_name
        self.my_roles = my_roles
        if kw:
            self.kw = kw
        else:
            self.kw = {}
        self.error_message = error_message
        self.reference = reference

    def toJSON(self):
        message_type = self.message_type
        ret = {}
        fn = lambda f: ret.update({f: getattr(self, f)})
        if message_type == '__event__':
            list(map(fn, self.event_fields))
        elif message_type == '__event_ack__':
            list(map(fn, self.event_ack_fields))
        elif message_type == '__event_nack__':
            list(map(fn, self.event_nack_fields))
        elif message_type == '__identity_card__':
            list(map(fn, self.identity_card_fields))
        elif message_type == '__identity_card_ack__':
            list(map(fn, self.identity_card_ack_fields))
        else:
            self.logger.info(
                'ERROR unknown message type %r' % message_type)
        return ret

    def copy(self, new_message_type):
        """ Copy the intra event to new message type
            with only the necessary fields to new type.
        """
        fields = {}
        fn = lambda f: fields.update({f: getattr(self, f)})
        if new_message_type == '__event__':
            list(map(fn, self.event_fields))
        elif new_message_type == '__event_ack__':
            list(map(fn, self.event_ack_fields))
        elif new_message_type == '__event_nack__':
            list(map(fn, self.event_nack_fields))
        elif new_message_type == '__identity_card__':
            list(map(fn, self.identity_card_fields))
        elif new_message_type == '__identity_card_ack__':
            list(map(fn, self.identity_card_ack_fields))
        else:
            self.logger.info(
                'ERROR unknown message type %r' % new_message_type)
        fields.update({'message_type': new_message_type})
        new = IntraEvent(**fields)
        return new

    def __repr__(self):
        return "%r" % self.toJSON()


class StaticRoute(object):
    """ Static route (when we are clients)
    """
    def __init__(self, name, roles, urls, connex):
        self.gaplic_name = name
        if isinstance(roles, (list, tuple,)):
            self.roles = roles
        elif roles:
            self.roles = [roles]
        else:
            self.roles = []
        if isinstance(urls, (list, tuple)):
            self.urls = urls
        else:
            self.urls = [urls]
        if not self.urls:
            raise ValueError(
                'StaticRoute needs urls'
            )

        connex.route = self
        self.connex = connex
        self.idx_url = 0        # current url connection if client
        self.dl_output_events = deque()  # queue of pending output events
        self.cur_pending_event = None
        self.write = None
        self.route_ref = hash(connex)
        self.identity_ack = False
        self.serial = 0
        self.ws = None
        self.their_roles = None  # their roles anwered in identity ack (with *)

    def incr_serial(self):
        self.serial += 1
        if self.serial > 10:
            self.serial = 1
        return self.serial

    def __str__(self):
        return "%s %s" % (self.gaplic_name, self.route_ref)

    def __repr__(self):
        return "\nSTATIC ROUTE:\n  gaplic_name: %s\n  roles: %s\n  " \
            "route_ref: %s\n  connex: %s\n  their_roles: %s\n" % (
                self.gaplic_name,
                self.roles,
                self.route_ref,
                self.connex.config.destinations,
                self.their_roles,
            )


class DynamicRoute(object):
    """ Dynamic route (when we are servers)
    """
    def __init__(self, name, roles, write, gsock):
        self.gaplic_name = name
        self.roles = roles
        if isinstance(roles, (list, tuple,)):
            self.roles = roles
        elif roles:
            self.roles = [roles]
        else:
            self.roles = []
        self.dl_output_events = deque()  # queue of pending output events
        self.cur_pending_event = None
        self.connex = None
        self.write = write
        self.gsock = gsock
        self.route_ref = hash(gsock)
        self.identity_ack = True
        self.serial = 0
        self.ws = None
        self.their_roles = None  # their roles anwered in identity (with ^)

    def incr_serial(self):
        self.serial += 1
        if self.serial > 10:
            self.serial = 1
        return self.serial

    def __str__(self):
        return "%s %s" % (self.gaplic_name, self.route_ref)

    def __repr__(self):
        return "\DINAMYC ROUTE:\n  gaplic_name: %s\n  roles: %s\n  " \
            "route_ref: %s\n  gsock: %r\n  their_roles: %r\n" % (
                self.gaplic_name,
                self.roles,
                self.route_ref,
                self.gsock,
                self.their_roles,
            )


class EmptyRoute(object):
    """ Empty route
    """
    def __init__(self):
        self.route_ref = None
        self.identity_ack = False

    def __str__(self):
        return "%s" % (self.route_ref)

    def __repr__(self):
        return "\EMPTY ROUTE:\n  route_ref: %s\n" % (
            self.route_ref,
        )


class GAplicRegistry(object):
    """ GAplics registry.
    """
    def __init__(self, router):
        self.router = router
        self.my_gaplic_name = router.gaplic.name  # self gaplic name
        self.my_roles = router.gaplic.roles  # self role
        self.static_routes = {}
        self.dynamic_routes = {}
        self.broadcasted_roles = []

    def add_static_route(self, name, roles, urls, connex_mode=None):
        if not isinstance(urls, (list, tuple)):
            urls = [urls]
        destinations = get_host_port_from_urls(urls)
        if not destinations:
            return None
        connex = self.router.create_gobj(
            'static_route',
            GConnex,
            self.router,
            transmit_ready_event_name=None,
            destinations=destinations,
        )
        r = StaticRoute(name, roles, urls, connex)
        self.static_routes[r.route_ref] = r
        return r

    def add_dynamic_route(self, name, role, write, gsock):
        if not name:
            # anonymous gaplic name
            name = "^%s%s" % (gsock.get_peername(), gsock.get_sockname())
        r = DynamicRoute(name, role, write, gsock)
        self.dynamic_routes[r.route_ref] = r
        return r

    def get_route_by_ref(self, route_ref):
        route = self.static_routes.get(route_ref, None)
        if not route:
            route = self.dynamic_routes.get(route_ref, None)
        return route

    def search_route(self, gaplic_name, role):
        registry = self

        #------------------------------#
        #   Search by gaplic_name
        #------------------------------#

        # search in static routes
        static_routes = registry.static_routes
        for route_ref in static_routes:
            route = static_routes[route_ref]
            if route.gaplic_name == gaplic_name:
                return route

        # search in dynamic routes
        dynamic_routes = registry.dynamic_routes
        for route_ref in dynamic_routes:
            route = dynamic_routes[route_ref]
            if route.gsock.is_disconnected():
                continue
            if route.gaplic_name == gaplic_name:
                return route

        #------------------------------#
        #   Search by role
        #------------------------------#

        # search in static routes
        static_routes = registry.static_routes
        for route_ref in static_routes:
            route = static_routes[route_ref]
            roles = route.roles
            for ro in roles:
                if ro == role:
                    return route

        # search in dynamic routes
        dynamic_routes = registry.dynamic_routes
        for route_ref in dynamic_routes:
            route = dynamic_routes[route_ref]
            if route.gsock.is_disconnected():
                continue
            roles = route.roles
            # TODO: busca el rol conectado si hay varios
            for ro in roles:
                ro = ro.lstrip('^')  # TODO: search removing ^ one to one
                if ro == role:
                    return route

        return None

    def enqueue_pending_event(self, route, intra_event):
        dl_output_events = route.dl_output_events
        ln = len(dl_output_events)
        if ln > self.router.config.limit_pending_output:
            self.router.logger.error("ERROR output event queue FULL: %d" % ln)
            self.check_route(route)
            return False
        dl_output_events.append(intra_event)
        return True

    def check_route(self, route):
        if isinstance(route, DynamicRoute):
            if route.gsock.is_closed() or route.gsock.is_disconnected():
                self.delete_route(route.route_ref)

    def delete_route(self, route_ref):
        key = route_ref
        dicc = self.dynamic_routes
        if key in dicc:
            self.router.logger.info("DELETING dynamic ROUTER %r" % (key))
            route = dicc[key]
            if route.ws:
                GObj.destroy_gobj(route.ws)
                route.ws = None
            del dicc[key]
            return True
        dicc = self.static_routes
        if key in dicc:
            self.router.logger.info("DELETING static ROUTER %r" % (key))
            route = dicc[key]
            if route.ws:
                GObj.destroy_gobj(route.ws)
                route.ws = None
            del dicc[key]
            return True
        return False

    def fire_pending_events(self, route):
        if not route.route_ref:
            return
        write = route.write
        trace_router = self.router.config.trace_router

        if not write:
            if trace_router:
                self.router.logger.info("    * route DISCONNECTED!!")
            return False

        if not route.identity_ack:
            # TODO: improve sending identity card with timeouts
            self.router.send_identity_card(route)
            return

        if route.cur_pending_event:
            try:
                msg = route.cur_pending_event.toJSON()
            except Exception as e:
                self.router.logger.exception(e)
                route.cur_pending_event = None  # trash message
                return False
            if trace_router:
                prefix = '%s ==> %s' % (
                    self.my_gaplic_name, route)
                self.router.trace_intra_event(prefix, route.cur_pending_event)
            write(msg)
            return True

        dl_output_events = route.dl_output_events
        if len(dl_output_events) > 0:
            route.cur_pending_event = dl_output_events.popleft()
            try:
                msg = route.cur_pending_event.toJSON()
            except Exception as e:
                self.router.logger.exception(e)
                route.cur_pending_event = None  # trash message
                return False
            if trace_router:
                prefix = '%s ==> %s' % (
                    self.my_gaplic_name, route)
                self.router.trace_intra_event(prefix, route.cur_pending_event)
            write(msg)
            return True
        return False

    def subcontracted_roles(self):
        """ Roles of static routes are our subcontracted roles
        """
        registry = self
        found_roles = set()

        # search in static routes
        static_routes = registry.static_routes
        for route_ref in static_routes:
            route = static_routes[route_ref]
            for ro in route.roles:
                found_roles.add(ro)

        found_roles = list(found_roles)
        return tuple(map(lambda x: '*' + x, found_roles))

    def get_roles_back_way(self):
        registry = self
        found_roles = set()

        # search in dynamic routes
        dynamic_routes = registry.dynamic_routes
        for route_ref in dynamic_routes:
            route = dynamic_routes[route_ref]
            if route.gsock.is_disconnected():
                continue
            roles = route.roles
            for ro in roles:
                found_roles.add(ro)
        found_roles = list(found_roles)
        return tuple(map(lambda x: '^' + x, found_roles))

    def check_broadcast_roles_back_way(self, roles):
        #broadcasted_roles = self.broadcasted_roles  # TODO: must be per route
        broadcasted_roles = []
        to_broadcast = []

        pure_roles = list(
            map(lambda x: x.lstrip('^'), roles)
        )

        for idx, ro in enumerate(pure_roles):
            if ro in self.my_roles:
                continue  # avoid loops
            if not ro in broadcasted_roles:
                to_broadcast.append('^' + roles[idx])
                broadcasted_roles.append(ro)

        if to_broadcast:
            self.broadcast_role_back_way(to_broadcast)

    def broadcast_role_back_way(self, roles_back_way):
        registry = self
        if self.router.config.trace_router:
            self.router.logger.info(
                "BROADCAST BACK WAY ====> %r" % roles_back_way)
        # search in static routes
        static_routes = registry.static_routes
        for route_ref in static_routes:
            route = static_routes[route_ref]
            if route.connex.is_disconnected():
                continue
            self.router.send_identity_card(route, roles_back_way)

    def role_level(self, role):
        role = role.strip()
        level = 0
        for level, char in enumerate(role):
            if not role[level] in ('^', '*'):
                break
        return level, role[level:]


class RouterConnection(SockJSConnection):
    """ Websocket application to work with Pyramid router.

    The messages come by here when the router server is a Pyramid web server.
    """
    clients = set()

    def on_open(self, info):
        session = self.session
        if session:
            session.write = session.send_message
            session.gsock = session.handler.gsock

    def on_message(self, msg):
        session = self.session
        router = session.gaplic.router
        try:
            msg = json_decode(msg)
        except Exception as e:
            router.logger.exception("ERROR %s:\n%s" % (e, hexdump('<==', msg)))
            return
        router.send_event(
            router,
            'EV_INPUT_MESSAGE',
            msg=msg,
            session=session,
        )

    def on_close(self):
        session = self.session
        router = session.gaplic.router
        route = session.route
        if route:
            router.registry.delete_route(route.route_ref)
        else:
            pass  # TODO: delete gsock or channel


def get_first_name(name):
    if '^' in name:
        name = name.split()[0]
    return name


def ac_connected(self, event):
    """ Someone is connected.
    By here we receive the connection of both client and server routers
    that are not pyramid routes.
    The GWebSocket gobj will take possession of all their events.
    """
    gsock = event.gsock
    source_gobj = event.source[-1]
    if hasattr(event, 'connex'):
        # client connection
        connex = event.connex
        route_ref = hash(connex)
        route = self.registry.get_route_by_ref(route_ref)
        # all urls must have the same path!!
        resource = get_path_from_url(route.urls[0])
        if not resource:
            resource = '/'
        ws = self.create_gobj(
            'websock_cli-' + source_gobj.name,
            GWebSocket,
            self,
            gsock=connex,
            iam_server=False,
            subscriber=self,
            resource=resource,
        )
        ws.route_ref = route_ref
        ws.route = route
        route.ws = ws
        route.write = ws.send_jsonfied_message

    else:
        # clisrv connection
        ws = self.create_gobj(
            'websock_srv-' + source_gobj.name,
            GWebSocket,
            self,
            gsock=gsock,
            iam_server=True,
            subscriber=self,
        )
        ws.route_ref = None
        ws.route = None


def ac_disconnected(self, event):
    """
    """


def ac_add_static_route(self, event):
    """ Add external gaplic.
    """
    name = event.kw.get('name', None)
    roles = event.kw.get('roles', '')
    urls = event.urls
    connex_mode = event.kw.get('connex_mode', None)

    route = self.registry.add_static_route(name, roles, urls, connex_mode)
    if not route:
        return -1
    if self.config.trace_router:
        self.logger.info("%s: NEW STATIC route: %r" % (
            self.registry.my_gaplic_name,
            route
        ))
    return route.route_ref


def ac_on_open(self, event):
    """
    By here we receive from both client and server routers
    that are not pyramid routes.
    """
    ws = event.source[-1]
    ws.write = ws.send_jsonfied_message

    # send our identity card if iam client
    # we only send the identity card in static routes!
    if not ws.config.iam_server:
        self.send_identity_card(ws.route)


def ac_on_close(self, event):
    """
    By here we receive from both client and server routers
    that are not pyramid routes.
    """
    ws = event.source[-1]
    route = ws.route
    if isinstance(route, DynamicRoute):
        self.registry.delete_route(route.route_ref)


def ac_on_message(self, event):
    """
    By here we receive from both client and server routers
    that are not pyramid routes.
    """
    ws = event.source[-1]
    msg = event.data

    try:
        msg = json_decode(msg)
    except Exception as e:
        self.logger.exception(
            "ERROR json_decode %s:\n%s" % (e, hexdump('<==', msg)),
        )
        return
    self.send_event(
        self,
        'EV_INPUT_MESSAGE',
        msg=msg,
        websocket=ws,
    )


def ac_input_message(self, event):
    """ Event attributes:
        * :attr:`msg`: received message.
    """
    registry = self.registry
    msg = event.msg
    try:
        intra_event = IntraEvent(**msg)
    except Exception as e:
        self.logger.error(
            "ERROR %s:\n%s" % (e, hexdump('<==', msg)),
            exc_info=True,
        )
        return
        raise
    message_type = intra_event.message_type
    trace_router = self.config.trace_router
    this_route = EmptyRoute()
    session = event.kw.get('session', None)  # entry by pyramid
    websocket = event.kw.get('websocket', None)  # entry by direct websocket
    if session:
        write = session.write
        gsock = session.gsock
        if hasattr(session, 'route'):
            if session.route:
                this_route = session.route
    elif websocket:
        write = websocket.write
        gsock = websocket.gsock
        if websocket.route:
            this_route = websocket.route

    if trace_router:
        prefix = '%s <== %s' % (
            registry.my_gaplic_name,
            this_route,
        )
        self.trace_intra_event(prefix, intra_event)

    if message_type == '__identity_card__':
        # Register a dynamic router
        gaplic_name = intra_event.my_gaplic_name
        roles = intra_event.my_roles
        if isinstance(this_route, EmptyRoute):
            # new dynamic route
            case = 'NEW'
            this_route = registry.add_dynamic_route(
                gaplic_name,
                roles,
                write,
                gsock,
            )
            if session:
                session.route = this_route
            elif websocket:
                websocket.route = this_route
                this_route.ws = websocket
            else:
                self.logger.error("ERROR no session neither websocket")
        else:
            # update dynamic route
            case = 'UPDATE'
            this_route.roles = roles  # TODO: check roles?

        if self.config.trace_router:
            self.logger.info("%s: %s DYNAMIC route: %s: %s: %s: %s" % (
                registry.my_gaplic_name,
                case,
                this_route.route_ref,
                this_route.gaplic_name,
                this_route.roles,
                gsock.addr))

        ack = IntraEvent(
            message_type='__identity_card_ack__',
            my_gaplic_name=registry.my_gaplic_name,
            my_roles=registry.my_roles + registry.subcontracted_roles(),
        )
        if trace_router:
            prefix = '%s ==> %s' % (
                registry.my_gaplic_name, this_route)
            self.trace_intra_event(prefix, ack)
        write(ack.toJSON())

        #
        #   Broadcast forward the new role's back ways.
        #
        registry.check_broadcast_roles_back_way(this_route.roles)

        #
        #   Somebody can be interested in know new clients
        #
        if case == 'NEW':
            self.broadcast_event(
                'EV_NEW_DYNAMIC_ROUTE',
                gaplic_name=gaplic_name,
                roles=roles,
            )

        return

    elif message_type == '__identity_card_ack__':
        # TODO: check if the info we have is correct
        this_route.identity_ack = True
        if intra_event.my_gaplic_name:
            if this_route.gaplic_name != intra_event.my_gaplic_name:
                self.logger.info(
                    "WARNING: updating route %r, GAPLIC_NAME! to %r" % (
                    this_route.route_ref,
                    intra_event.my_gaplic_name))
                this_route.gaplic_name = intra_event.my_gaplic_name

        # check their roles
        for r in intra_event.my_roles:
            if not r in this_route.roles:
                if self.config.update_unknown_roles:
                    self.logger.warn(
                        "WARNING: updating route %r, adding ROLE %r" % (
                        this_route.route_ref,
                        r))
                    this_route.roles.append(r)

        # check if our subcontracted roles are all
        for r in this_route.roles:
            pure_roles = list(
                map(lambda x: x.lstrip('*'), intra_event.my_roles)
            )
            if not r in pure_roles:
                self.logger.error(
                    "ERROR: %r LACKS role %r, it has only %r" % (
                    this_route,
                    r,
                    intra_event.my_roles))
        this_route.their_roles = intra_event.my_roles[:]

        if self.config.trace_router:
            self.logger.info("%s: UPDATE STATIC route: %r" % (
                self.registry.my_gaplic_name,
                this_route
            ))

        registry.fire_pending_events(this_route)
        return

    elif message_type == '__event_ack__' or message_type == '__event_nack__':
        if this_route.route_ref:
            cur_pending_event = this_route.cur_pending_event
            if not cur_pending_event:
                self.logger.error("ERROR processing ack: NO cur_pending_event")

            if cur_pending_event and \
                    intra_event.serial != cur_pending_event.serial:
                self.logger.error("ERROR processing ack: DIFFERENT SERIAL")

            del this_route.cur_pending_event
            this_route.cur_pending_event = None
            registry.fire_pending_events(this_route)
        return

    elif message_type == '__event__':
        #--------------------------------------------------#
        #   It's an event. Search if for us or to resend
        #--------------------------------------------------#
        own = False

        if isinstance(this_route, DynamicRoute):
            if not intra_event.origin_gaplic:
                #  Set our extended gaplic name
                intra_event.origin_gaplic = this_route.gaplic_name

        # search by gaplic
        if intra_event.destination_gaplic and registry.my_gaplic_name:
            first_gaplic_name = get_first_name(intra_event.destination_gaplic)
            if first_gaplic_name == registry.my_gaplic_name:
                own = True

        # search by role
        if intra_event.destination_role and registry.my_roles:
            if intra_event.destination_role in registry.my_roles:
                own = True

        if own:
            #------------------------------------#
            #   The event is for own gaplic.
            #------------------------------------#
            dst_gobj = intra_event.destination_gobj
            try:
                named_gobj = self.gaplic.find_unique_gobj(dst_gobj)
            except GObjError as e:
                ack = intra_event.copy('__event_nack__')
                ack.error_message = e
                if trace_router:
                    prefix = '%s ==> %s' % (
                        registry.my_gaplic_name, this_route)
                    self.trace_intra_event(prefix, ack)
                write(ack.toJSON())
                return

            if not named_gobj:
                ack = intra_event.copy('__event_nack__')
                ack.error_message = "GObj %r UNKNOWN" % dst_gobj
                if trace_router:
                    prefix = '%s ==> %s' % (
                        registry.my_gaplic_name, this_route)
                    self.trace_intra_event(prefix, ack)
                write(ack.toJSON())
                return

            if trace_router:
                self.logger.info("   !!! IntraEvent MINE !!!")

            if intra_event.kw.get('__subscribe_event__', False):
                # it's a external subscription
                external_subscriptor_ref = self.make_external_subscription(
                    intra_event,
                    this_route.route_ref
                )
                if not external_subscriptor_ref:
                    ack = intra_event.copy('__event_nack__')
                    ack.error_message = "Cannot make external subscription"
                    if trace_router:
                        prefix = '%s ==> %s' % (
                            registry.my_gaplic_name, this_route)
                        self.trace_intra_event(prefix, ack)
                    write(ack.toJSON())
                    return

                subs_kw = {
                    '__rename_event_name__': 'EV_SUBSCRIPTION',
                    '__subscription_reference__': external_subscriptor_ref,
                }
                try:
                    isubscription = named_gobj.subscribe_event(
                        intra_event.event_name,
                        self,
                        **subs_kw
                    )
                except Exception as e:
                    self.remove_external_subscription(external_subscriptor_ref)
                    ack = intra_event.copy('__event_nack__')
                    ack.error_message = "Cannot subscribe event: %s" % e
                    if trace_router:
                        prefix = '%s ==> %s' % (
                            registry.my_gaplic_name, this_route)
                        self.trace_intra_event(prefix, ack)
                    write(ack.toJSON())
                    return
                esubscription = self.get_external_subscription(
                    external_subscriptor_ref)
                esubscription.isubscription = isubscription

                # simple ack, no checkout, for the sender could remove the msg.
                ack = intra_event.copy('__event_ack__')
                ack.reference = external_subscriptor_ref
                if trace_router:
                    prefix = '%s ==> %s' % (
                        registry.my_gaplic_name, this_route)
                    self.trace_intra_event(prefix, ack)
                write(ack.toJSON())
                return

            if intra_event.kw.get('__unsubscribe_event__', False):
                # it's a external unsubscription
                subscription_reference = intra_event.kw.get(
                    '__subscription_reference__', None)

                if subscription_reference:
                    self.remove_external_subscription(subscription_reference)
                else:
                    # TODO: find and delete external subscription
                    self.logger.error("ERROR no __subscription_reference__")

                # simple ack, no checkout, for the sender could remove the msg.
                ack = intra_event.copy('__event_ack__')
                if trace_router:
                    prefix = '%s ==> %s' % (
                        registry.my_gaplic_name, this_route)
                    self.trace_intra_event(prefix, ack)
                write(ack.toJSON())
                return

            # simple ack, no checkout, for the sender could remove the msg.
            ack = intra_event.copy('__event_ack__')
            if trace_router:
                prefix = '%s ==> %s' % (
                    registry.my_gaplic_name, this_route)
                self.trace_intra_event(prefix, ack)
            write(ack.toJSON())

            # inject the event in the gaplic
            ret = self.send_event(
                named_gobj,
                intra_event.event_name,
                __intra_event__=intra_event,
                **intra_event.kw
            )

            # send action resp as event if they subscribe it.
            if intra_event.kw.get('__subscribe_response__', False):
                resp = IntraEvent(
                    message_type='__event__',
                    route_ref=None,
                    serial=this_route.incr_serial(),
                    event_name=intra_event.event_name,
                    destination_gaplic=intra_event.origin_gaplic,
                    destination_gobj=intra_event.origin_gobj,
                    origin_gaplic=registry.my_gaplic_name,
                    origin_gobj=named_gobj.name,
                    kw={
                        '__action_return__': ret,
                    }
                )

                registry.enqueue_pending_event(
                    this_route,
                    resp,
                )
                if not this_route.cur_pending_event:
                    registry.fire_pending_events(this_route)

            return

        #-------------------------------------------#
        #       The event is for resend.
        #       Search in routes.
        #-------------------------------------------#
        route_dst = registry.search_route(
            intra_event.destination_gaplic,
            intra_event.destination_role)

        if not route_dst:
            # nothing found
            ack = intra_event.copy('__event_nack__')
            ack.error_message = "Destination gaplic %r or role % r" \
                " NOT FOUND" % (
                    intra_event.destination_gaplic,
                    intra_event.destination_role
                )
            if trace_router:
                prefix = '%s ==> %s' % (
                    registry.my_gaplic_name, this_route)
                self.trace_intra_event(prefix, ack)
            write(ack.toJSON())
            return

        if trace_router:
            self.logger.info("    * IntraEvent FORWARD!!")

        if not route_dst.write:
            # nothing found
            ack = intra_event.copy('__event_nack__')
            ack.error_message = "Route found but DISCONNECTED"
            if trace_router:
                prefix = '%s ==> %s' % (
                    registry.my_gaplic_name, this_route)
                self.trace_intra_event(prefix, ack)
            write(ack.toJSON())
            return

        # enqueue the action response event
        ret = registry.enqueue_pending_event(
            route_dst,
            intra_event,
        )
        # simple ack, no checkout, for the sender could remove the msg.
        if ret:
            ack = intra_event.copy('__event_ack__')
        else:
            ack = intra_event.copy('__event_nack__')
            if trace_router:
                self.logger.info("    * event queue FULL!!")
            ack.error_message = "route_dst event queue FULL"
        if trace_router:
            prefix = '%s ==> %s' % (
                registry.my_gaplic_name, this_route)
            self.trace_intra_event(prefix, ack)
        write(ack.toJSON())

        if not route_dst.cur_pending_event:
            registry.fire_pending_events(route_dst)
        else:
            if ret:
                if trace_router:
                    self.logger.info("    * route_dst BUSY!!")

    else:
        self.logger.error("=================================================")
        self.logger.error("ERROR message_type UNKNOWN: %r" % message_type)


def ac_timeout(self, event):
    something_todo = self.check_routes()
    if something_todo:
        self.set_timeout(self.config.timeout_idle)


def ac_show_routes(self, event):
    ret = self.mt_show_routes()
    return ret


def ac_command(self, event):
    command = event.command
    ret = self.mt_execute_command(command)
    return ret


def ac_subscription(self, event):
    subscription_reference = event.__subscription_reference__
    subscription = self.external_subscriptions.get(
        subscription_reference, None)
    if subscription:
        self._send_event_to_external_route(
            subscription.route_ref,
            subscription.origin_gaplic,
            subscription.origin_role,
            subscription.origin_gobj,
            subscription.event_name,
            subscription.destination_gobj,
            event.kw)


def ac_send_event_outside(self, event):
    gaplic_name = event.gaplic_name
    role = event.role
    gobj_name = event.gobj_name
    event_name_ = event.event_name_
    subscriber_gobj = event.subscriber_gobj
    origin_role = event.origin_role
    kw = event.kw

    registry = self.registry
    route = registry.search_route(gaplic_name, role)
    if not route:
        self.logger.error(
            "ERROR ac_send_event_outside() "
            "route NOT FOUND: %r %r" % (gaplic_name, role))
        return False

    intra_event = IntraEvent(
        message_type='__event__',
        serial=route.incr_serial(),
        event_name=event_name_,
        destination_gaplic=gaplic_name,
        destination_role=role,
        destination_gobj=gobj_name,
        origin_gaplic=registry.my_gaplic_name,
        origin_role=origin_role if origin_role else registry.my_roles[0],
        origin_gobj=subscriber_gobj,
        kw=kw)

    registry.enqueue_pending_event(route, intra_event)
    if not route.cur_pending_event:
        registry.fire_pending_events(route)
    return True


GROUTER_FSM = {
    'event_list': (
        'EV_ADD_STATIC_ROUTE: top input',
        'EV_COMMAND: top input',
        'EV_SHOW_ROUTES: top input',
        'EV_CONNECTED: bottom input',
        'EV_DISCONNECTED: bottom input',
        'EV_ON_OPEN: bottom input',
        'EV_ON_CLOSE: bottom input',
        'EV_ON_MESSAGE: bottom input',
        'EV_INPUT_MESSAGE: bottom input',
        'EV_TIMEOUT: bottom input',
        'EV_SUBSCRIPTION: bottom input',
        'EV_SEND_EVENT_OUTSIDE: top input',
        'EV_NEW_DYNAMIC_ROUTE: top output',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_COMMAND',              ac_command,             None),
            ('EV_SHOW_ROUTES',          ac_show_routes,         None),
            ('EV_ADD_STATIC_ROUTE',     ac_add_static_route,    None),
            ('EV_CONNECTED',            ac_connected,           None),
            ('EV_DISCONNECTED',         ac_disconnected,        None),
            ('EV_ON_OPEN',              ac_on_open,             None),
            ('EV_ON_CLOSE',             ac_on_close,            None),
            ('EV_ON_MESSAGE',           ac_on_message,          None),
            ('EV_INPUT_MESSAGE',        ac_input_message,       None),
            ('EV_TIMEOUT',              ac_timeout,             None),
            ('EV_SUBSCRIPTION',         ac_subscription,        None),
            ('EV_SEND_EVENT_OUTSIDE',   ac_send_event_outside,  None),
        ),
    }
}


def validate_static_routes(value):
    """
    sca1, sca+sca, http://localhost:8002+http://localhost:8002;
    sca2, sca+sca, http://localhost:8003+http://localhost:8003;

    must convert in:

    ((
        'sca1',
        ('sca','sca'),
        ('http://localhost:8002', 'http://localhost:8002'),
    ),
    (
        'sca2',
        ('sca','sca'),
        ('http://localhost:8003', 'http://localhost:8003'),
    ))

    """
    routes = []
    if value:
        # save each route separated by ;
        value = value.split(';')
        for r in value:
            r = r.strip()
            if r:
                routes.append(r)

        # split each route by ,
        for idx, r in enumerate(routes):
            items = r.split(',')
            v = []
            for it in items:
                it = it.strip()
                if it:
                    v.append(it)
            routes[idx] = v

        for r in routes:
            for idx, field in enumerate(r):
                v = ()
                if not '+' in field:
                    v += (field,)
                    continue
                items = field.split('+')
                for e in items:
                    e = e.strip()
                    if e:
                        v += (e,)
                r[idx] = v

    return routes


GROUTER_GCONFIG = {
    #TODO: dns router with a short range ports?
    'server': [
        bool, False, 0, None,
        'Server router. Any gaplic with public services must be server'
    ],
    'localhost_route_ports': [
        tuple, range(2690, 2700), 0, None,
        'List of posible listening ports acting as localhost tcp router server'
    ],
    'pyramid_router_url': [
        str, '__pyramid_router__', 0, None,
        'pyramid url to start the router'
    ],
    'pyramid_root': [None, None, 0, None, 'pyramid root (parent)'],
    'trace_router': [bool, False, 0, None, "trace route messages"],
    'limit_pending_output': [int, 2, 0, None, "output queue size"],
    'timeout_idle': [int, 5, 0, None, "idle timeout"],
    'static_routes': [
        tuple, None, 0, validate_static_routes,
        'static routes with format:'
        'name, role1+role2, url1+url2; name2, role2, url2; ...'
    ],
    'update_unknown_roles': [bool, False, 0, None, "update unknown roles"],
}


class GRouter(GObj):
    """  GRouter GObj.
    Exchange events between GAplic's of same or different hosts.
    This gobj is permanent and direct child of his GAplic.

    The GRouter have two options:

    * open an own listening port,
    * use a url in a http server environment.

    The first option only works with a pure websocket channel.
    The second option needs an application done with Pyramid framework
    and implements sockjs-protocol.

    .. ginsfsm::
       :fsm: GROUTER_FSM
       :gconfig: GROUTER_GCONFIG

    *Input-Events:*
        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_CONNECTED'`: New client.

        * :attr:`'EV_DISCONNECTED'`: Client disconnected.

    *Output-Events:*

    """
    def __init__(self):
        GObj.__init__(self, GROUTER_FSM, GROUTER_GCONFIG)
        self.server_sock = None  # server sock of tcp router
        self.local_router = None
        self.external_subscriptions = {}

    def start_up(self):
        """ Initialization zone.
        """
        self.registry = GAplicRegistry(self)
        if self.config.pyramid_router_url:
            # router inside pyramid.
            self.sockjs = self.create_gobj(
                self.config.pyramid_router_url,       # named gobj
                GSockjsServer,          # gclass
                self.config.pyramid_root,      # parent
                sockjs_app_class=RouterConnection,
                response_limit=4096,
                #disabled_transports=('websocket',)  # we need support IE8
            )
        elif self.config.server:
            # router with server sock
            self.start_router_server()

        self._timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')
        self.set_timeout(self.config.timeout_idle)

        if self.config.static_routes:
            routes = self.config.static_routes
            for r in routes:
                name, roles, urls = r
                self.send_event(
                    self,
                    'EV_ADD_STATIC_ROUTE',
                    name=name,
                    roles=roles,
                    urls=urls,
                )

    def set_timeout(self, seconds):
        if self._timer:  # protect from overwrite_parameters
            self.send_event(self._timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        if self._timer:  # protect from overwrite_parameters
            self.send_event(self._timer, 'EV_SET_TIMER', seconds=-1)

    def mt_execute_command(self, command):
        ret = 'EXECUTED ' + command + ' Ok'
        return ret

    def mt_show_routes(self):
        registry = self.registry
        s = 'My gaplic name: %r\n' % registry.my_gaplic_name
        s += 'My roles: %r\n\n' % registry.my_roles
        static_routes = registry.static_routes
        s += 'Static routes:\n'
        for key in static_routes:
            r = static_routes[key]
            name = r.gaplic_name
            roles = r.roles
            urls = r.urls
            acked = 'Yes Acked' if r.identity_ack else 'NOT Acked'
            s += '  route_ref: %-12s | name:%r | roles:%r | %s | %s\n' % (
                key,
                name,
                roles,
                urls,
                acked,
            )
        s += '\n'

        s += 'Dynamic routes:\n'
        dynamic_routes = registry.dynamic_routes
        for key in dynamic_routes:
            r = dynamic_routes[key]
            name = r.gaplic_name
            roles = r.roles
            s += '  route_ref: %-12s | name:%s | roles:%s\n' % (
                key, name, roles)
        s += '\n'
        return s

    def check_routes(self):
        registry = self.registry
        static_routes = registry.static_routes
        ret = False
        for key in static_routes:
            r = static_routes[key]
            if not r.identity_ack:
                # TODO: retransmite la identity si timeout
                ret = True

            # TODO: retransmite cur_pending_event si timeout

        dynamic_routes = registry.dynamic_routes
        for key in dynamic_routes:
            r = dynamic_routes[key]
            # TODO: retransmite cur_pending_event si timeout
            pass

        return ret

    def trace_intra_event(self, prefix, intra_event):
        hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_type = intra_event.message_type

        if message_type == '__event__':
            fields = intra_event.event_fields
        elif message_type == '__event_ack__':
            fields = intra_event.event_ack_fields
        elif message_type == '__event_nack__':
            fields = intra_event.event_nack_fields
        elif message_type == '__identity_card__':
            fields = intra_event.identity_card_fields
        elif message_type == '__identity_card_ack__':
            fields = intra_event.identity_card_ack_fields
        else:
            self.logger.info(
                'ERROR unknown message type %r' % message_type)

        try:
            trace = "\n%s %s\n" % (
                hora,
                prefix,
            )
            for f in fields:
                trace += "    %s: %r\n" % (f, getattr(intra_event, f))
            self.logger.info(trace)

        except Exception as e:
            self.logger.error(
                "ERROR %s:\n%r" % (e, intra_event),
                exc_info=True,
            )

    def send_identity_card(self, route, roles_back_way=None):
        my_gaplic_name = self.registry.my_gaplic_name
        my_roles = self.registry.my_roles
        if roles_back_way:
            my_roles_back_way = roles_back_way
            prefix = '%s ^==> %s' % (my_gaplic_name, route)
        else:
            my_roles_back_way = self.registry.get_roles_back_way()
            prefix = '%s ==> %s' % (my_gaplic_name, route)

        idc = IntraEvent(
            message_type='__identity_card__',
            route_ref=None,
            serial=None,
            my_gaplic_name=my_gaplic_name,
            my_roles=list(my_roles) + list(my_roles_back_way),
            kw={},
        )

        if self.config.trace_router:
            self.trace_intra_event(prefix, idc)
        x = idc.toJSON()
        route.write(x)

    def find_local_router(self):
        if self.local_router:
            return  # already created.

        ports = list(self.config.localhost_route_ports)
        if self.server_sock:
            # remove own port if iam-server
            try:
                index = ports.index(self.server_sock.port)
                ports.pop(index)
            except ValueError:
                pass

        destinations = list((lambda x: ('localhost', x), ports))
        self.local_router = self.create_gobj(
            'local_router_client',
            GConnex,
            self,
            transmit_ready_event_name=None,
            destinations=destinations,
        )

    def start_router_server(self):
        self.server_sock = self.create_gobj(
            self.gaplic.name + '-router',
            GServerSock,
            self,
            host='0.0.0.0',
            ports=self.config.localhost_route_ports,
            use_multi_ports=True,
            transmit_ready_event_name=None,
        )

    def _send_event_to_external_route(
            self,
            route_ref,
            gaplic_name,
            role,
            gobj_name,
            event_name,
            subscriber_gobj,
            kw):
        registry = self.registry
        route = registry.get_route_by_ref(route_ref)
        if not route:
            self.logger.error("ERROR route_ref NOT FOUND: %r" % route_ref)
            return False

        intra_event = IntraEvent(
            message_type='__event__',
            serial=route.incr_serial(),
            event_name=event_name,
            destination_gaplic=gaplic_name,
            destination_role=role,
            destination_gobj=gobj_name,
            origin_gaplic=registry.my_gaplic_name,
            origin_role=registry.my_roles,  # use destination_role?
            origin_gobj=subscriber_gobj,
            kw=kw)

        registry.enqueue_pending_event(route, intra_event)
        if not route.cur_pending_event:
            registry.fire_pending_events(route)
        return True

    def make_external_subscription(self, intra_event, route_ref):
        k = random_key()
        subscription = ExternalSubscription(intra_event, route_ref)
        self.external_subscriptions[k] = subscription
        return k

    def remove_external_subscription(self, subscription_reference):
        if subscription_reference in self.external_subscriptions:
            subs = self.external_subscriptions[subscription_reference]
            if subs:
                isubscription = subs.isubscription
                named_gobj = self.gaplic.find_unique_gobj(
                    subs.destination_gobj)
                if named_gobj:
                    named_gobj.delete_subscription_by_object(isubscription)
            del self.external_subscriptions[subscription_reference]

    def get_external_subscription(self, subscription_reference):
        if subscription_reference in self.external_subscriptions:
            subs = self.external_subscriptions[subscription_reference]
            return subs
