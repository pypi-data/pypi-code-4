
def _hello_world_context():
    return {
        'context' : 'Hello World!',
    }

def index(request):
    return _hello_world_context()

def test1(request):
    return _hello_world_context()

def test2(request):
    return _hello_world_context()

def test2_test3(request):
    return _hello_world_context()
