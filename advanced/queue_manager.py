from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
import json
import Queue



class Telephony(protocol.Protocol):

    def respond(self, *response):
        index = 0
        parsed_response=''
        while index < len(response)-1:
            parsed_response += response[index] + '\n'
            index+=1
        parsed_response += response[index]
        self.transport.write(parsed_response)

    def dataReceived(self, data):
        request = json.loads(data)
        command = request['command']
        id = request['id'].encode('ascii')

        if command=='call':
            response = self.call(id)
            self.respond(*response)
        elif command=='answer':
            response= self.answer(id)
            self.respond(*response)
        elif command=='reject':
            response = self.reject(id)
            self.respond(*response)
        elif command=='hangup':
            response = self.hangup(id)
            self.respond(*response)

    def ring(self, operator, call_id, response):
        self.factory.Operators[operator] = 'ringing'
        self.factory.ringingCalls[operator]=call_id
        response.append('Call ' + call_id + ' ringing for operator ' + operator)

    def ring_call(self, call_id, response):
        for operator, state in self.factory.Operators.iteritems():
            if state == 'available':
                self.ring(operator, call_id, response)
                return True

    def remove_from_queue(self, call):
        auxiliary_queue = Queue.Queue()
        while not self.factory.calls_waiting_queue.empty():
            queue_object = self.factory.calls_waiting_queue.get()
            if queue_object == call:
                while not self.factory.calls_waiting_queue.empty():
                    queue_object = self.factory.calls_waiting_queue.get()
                    auxiliary_queue.put(queue_object)
                while not auxiliary_queue.empty():
                    queue_object = auxiliary_queue.get()
                    self.factory.calls_waiting_queue.put(queue_object)
                return True
            auxiliary_queue.put(queue_object)
        while not auxiliary_queue.empty():
            queue_object = auxiliary_queue.get()
            self.factory.calls_waiting_queue.put(queue_object)
            return False

    def call(self, call_id):
        response = []
        response.append('Call ' + call_id + ' received')
        if self.ring_call(call_id,response):
            return response
        self.factory.calls_waiting_queue.put(call_id)
        response.append('Call ' + call_id + ' waiting in queue')
        return response

    def answer(self, operator_id):
        response = []
        call_id = self.factory.ringingCalls[operator_id]
        self.factory.Operators[operator_id]='busy'
        self.factory.ongoingCalls[call_id]=operator_id
        del self.factory.ringingCalls[operator_id]
        response.append('Call ' + call_id + ' answered by operator ' + operator_id)
        return response

    def reject(self, operator_id):
        response = []
        call_id = self.factory.ringingCalls[operator_id]
        del self.factory.ringingCalls[operator_id]
        response.append('Call ' + call_id + ' rejected by operator ' + operator_id)
        if self.ring_call(call_id, response):
            Operators[operator_id] = 'available'
            return response
        self.factory.ringingCalls[operator_id] = call_id
        response.append('Call ' + call_id + ' ringing for operator ' + operator_id)
        return response

    def hangup(self, call_id):
        response= []
        if call_id in self.factory.ongoingCalls:
            operator = self.factory.ongoingCalls[call_id]
            self.factory.Operators[operator]='available'
            del self.factory.ongoingCalls[call_id]
            response.append('Call ' + call_id + ' finished and operator ' + operator + ' available')
            if not self.factory.calls_waiting_queue.empty():
                 disenqueued_call_id = self.factory.calls_waiting_queue.get()
                 self.ring(operator, disenqueued_call_id, response)
                 return response
            return response
        else:
            for operator, respective_call in self.factory.ringingCalls.iteritems():
                if respective_call == call_id:
                    del self.factory.ringingCalls[operator]
                    response.append('Call ' +  call_id + ' missed')
                    if not self.factory.calls_waiting_queue.empty():
                        disenqueued_call_id = self.factory.calls_waiting_queue.get()
                        self.ring(operator, disenqueued_call_id, response)
                    return response
            if self.remove_from_queue(call_id):
                response.append('Call ' + call_id + ' missed')
                return response

class TelephonyFactory(protocol.Factory):
    def __init__(self):
        self.Operators = {'A':'available', 'B':'available'}  # operator:state
        self.ringingCalls = {}                               # operator:call_id
        self.ongoingCalls = {}                               # call_id:operator
        self.calls_waiting_queue = Queue.Queue()

    protocol = Telephony
