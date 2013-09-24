from publishers import publisher
from subscribers import subscriber
from constants import *
import time
import threading

def test_init_publisher():
    p=publisher('ipc:///tmp/test/0')
    assert p is not None
    assert p.sock() is not None
    p.close()
    
def test_init_subscriber():
    p=publisher('ipc:///tmp/test/0')
    def foo(topic, message):
        pass
    s=subscriber('ipc:///tmp/test/0',[''],foo,JSON)
    assert p is not None
    assert p.sock() is not None
    assert s is not None
    assert s.sock() is not None
    p.close()
    s.close()    
    
def test_init_basic_subscribe():
    m = threading.Condition()
    m.acquire()
    p=publisher('ipc:///tmp/test/0')
    def foo(topic, message):
        m.acquire()
        assert message == 'test message'
        m.notifyAll()
        m.release()
    s=subscriber('ipc:///tmp/test/0',['test'],foo,STRING)
    s.start()
    assert p is not None
    assert p.sock() is not None
    assert s is not None
    assert s.sock() is not None
    p.publish('test message',STRING,'test')
    m.wait() 
    m.release()
    s.stop()   
    s.close()        
    p.close()

