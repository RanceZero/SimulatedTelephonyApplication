from twisted.internet import protocol, reactor

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    protocol = Echo

reactor.listenTCP(5678, EchoFactory())
reactor.run()
