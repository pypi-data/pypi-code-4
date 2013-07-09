import js.strophe
from fanstatic import Library, Resource

library = Library('strophe.pubsub.js', 'resources')

strophe_pubsub = Resource(
    library, 'strophe.pubsub.js', depends=[js.strophe.strophe])
