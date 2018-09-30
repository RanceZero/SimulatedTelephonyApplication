from twisted.internet import reactor, protocol
from twisted.internet import stdio
from twisted.protocols import basic
import cmd
import json

class Cmd(cmd.Cmd):

    def do_call(self, arg):
        call_id = arg.split()[0]
        request = json.dumps({'command': 'call', 'id': call_id})
        return request

    def do_answer(self, arg):
        operator = arg.split()[0]
        request =  json.dumps({'command': 'answer', 'id': operator})
        return request

    def do_reject(self, arg):
        operator = arg.split()[0]
        request = json.dumps({'command': 'reject', 'id': operator})
        return request

    def do_hangup(self, arg):
        call=arg.split()[0]
        request = json.dumps({'command': 'hangup', 'id': call})
        return request

    def default(self, arg):
        args=arg.split()[0]
        if(args=='#'):
            return False
        print '*** Unknown syntax: ' + args
        return False

class Client(protocol.Protocol):
    def connectionMade(self):
        self.transport.write('hello man')

    def dataReceived(self, data):
        print 'Server said: ' + data
        self.transport.loseConnection()

class EchoFactory(protocol.ClientFactory):
    protocol = Client;

    def clientConnectionFailed(self, connector, reason):
        print "Connection Failed " + reason
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()

class InputReader(basic.LineReceiver):
    from os import linesep as delimiter
    def connectionMade(self):
        self.transport.write('>>> ')

    def lineReceived(self, line):
        request = Cmd.onecmd(line)
        if request:
            print request
        self.transport.write('>>> ')

Cmd=Cmd()
stdio.StandardIO(InputReader())
something = reactor.connectTCP("localhost", 5678, EchoFactory())
reactor.run()
