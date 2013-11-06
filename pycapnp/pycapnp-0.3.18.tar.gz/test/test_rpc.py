import pytest
import capnp
import os

this_dir = os.path.dirname(__file__)

@pytest.fixture
def capability():
     return capnp.load(os.path.join(this_dir, 'test_capability.capnp'))

'''

class RpcTest: public testing::Test {
protected:
  TestNetwork network;
  TestRestorer restorer;
  kj::SimpleEventLoop loop;
  RpcSystem<test::TestSturdyRef> rpcClient;
  RpcSystem<test::TestSturdyRef> rpcServer;

  Capability::Client connect(test::TestSturdyRef::Tag tag) {
    MallocMessageBuilder refMessage(128);
    auto ref = refMessage.initRoot<test::TestSturdyRef>();
    ref.setHost("server");
    ref.setTag(tag);

    return rpcClient.connect(ref);
  }

  RpcTest()
      : rpcClient(makeRpcClient(network.add("client"), loop)),
        rpcServer(makeRpcServer(network.add("server"), restorer, loop)) {}

  ~RpcTest() noexcept {}
  // Need to declare this with explicit noexcept otherwise it conflicts with testing::Test::~Test.
  // (Urgh, C++11, why did you change this?)
};
'''

class RpcTester:
    def __init__(self):
        # self.vat = VatNetwork...
        # self.restorer = SturdyRefRestorer...
        self.loop = capnp.EventLoop()
        self.rpcClient = makeRpcClient(self.network.add("client"), self.loop)
        self.rpcServer = makeRpcServer(self.network.add("server"), self.restorer, self.loop)

    def connect(self, tag):
        ref = capability().TestSturdyRef.new_message()
        ref.host = 'server'
        ref.tag = tag

        return self.rpcClient.connect(ref)
