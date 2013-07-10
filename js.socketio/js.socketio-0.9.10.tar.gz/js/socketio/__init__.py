from fanstatic import Library, Resource

library = Library('socketio', 'resources')
socketio = Resource(library, 'js/socket.io.js', minified='js/socket.io.min.js')
