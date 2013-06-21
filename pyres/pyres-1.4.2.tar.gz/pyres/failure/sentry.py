from raven import Client
def create(*args, **kwargs):
    client = Client()
    ident = client.get_ident(client.captureException())
    print ident
    return ident
