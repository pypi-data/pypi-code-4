from requestors import requestor
from repliers import replier
from constants import *
import time
import threading 

def test_init_requestor():
    def foo(message,requestor):
        pass
    rq=requestor('ipc:///tmp/test/0',foo,JSON)
    assert rq is not None
    assert rq.sock() is not None
    rq.close()
    
def test_init_replier():
    def foo(message,requestor):
        pass
    rq=requestor('ipc:///tmp/test/0',foo,JSON)
    rp=replier('ipc:///tmp/test/0',foo,JSON)
    assert rq is not None
    assert rq.sock() is not None
    assert rp is not None
    assert rp.sock() is not None
    rq.close()
    rp.close()    
    
def test_init_basic_reqrep():
    m = threading.Condition()
    m.acquire()
    def foo(message,requestor):
        m.acquire()
        assert message == 'test message'
        m.notifyAll()
        m.release()
    def foo1(message,replier):
        m.acquire()
        assert message == 'test message'
        replier.reply(message,JSON)
        m.notifyAll()
        m.release()
    rq=requestor('ipc:///tmp/test/0',foo,JSON)
    rp=replier('ipc:///tmp/test/0',foo1,JSON)
    rq.start()
    rp.start()
    assert rq is not None
    assert rq.sock() is not None
    assert rp is not None
    assert rp.sock() is not None
    rq.request('test message',JSON)
    m.wait()  
    m.release()  
    rq.stop()
    rp.stop()
    rq.close()
    rp.close()
