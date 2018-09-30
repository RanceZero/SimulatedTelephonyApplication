import cmd
import Queue

def ring(operator, call_id):
    Operators[operator] = 'ringing'
    ringingCalls[operator]=call_id
    print 'Call ' + call_id + ' ringing for operator ' + operator

def ring_call(call_id):
    for operator, state in Operators.iteritems():
        if state == 'available':
            ring(operator, call_id)
            return True

def remove_from_queue(call):
    auxiliary_queue = Queue.Queue()
    while not calls_waiting_queue.empty():
        queue_object = calls_waiting_queue.get()
        if queue_object == call:
            while not calls_waiting_queue.empty():
                queue_object = calls_waiting_queue.get()
                auxiliary_queue.put(queue_object)
            while not auxiliary_queue.empty():
                queue_object = auxiliary_queue.get()
                calls_waiting_queue.put(queue_object)
            return True
        auxiliary_queue.put(queue_object)
    while not auxiliary_queue.empty():
        queue_object = auxiliary_queue.get()
        calls_waiting_queue.put(queue_object)
        return False


class Cmd(cmd.Cmd):

    def do_call(self, arg):
        call_id = arg.split()[0]
        print 'Call ' + call_id + ' received'
        if ring_call(call_id):
            return
        calls_waiting_queue.put(call_id)
        print 'Call ' + call_id + ' waiting in queue'

    def do_answer(self, arg):
        operator = arg.split()[0]
        call_id = ringingCalls[operator]
        Operators[operator]='busy'
        ongoingCalls[call_id]=operator
        del ringingCalls[operator]
        print 'Call ' + call_id + ' answered by operator ' + operator

    def do_reject(self, arg):
        operator = arg.split()[0]
        call_id = ringingCalls[operator]
        del ringingCalls[operator]
        print 'Call ' + call_id + ' rejected by operator ' + operator
        if ring_call(call_id):
            Operators[operator] = 'available'
            return
        ringingCalls[operator] = call_id
        print 'Call ' + call_id + ' ringing for operator ' + operator

    def do_hangup(self, arg):
        call=arg.split()[0]
        if call in ongoingCalls:
            operator = ongoingCalls[call]
            Operators[operator]='available'
            del ongoingCalls[call]
            print 'Call ' + call + ' finished and operator ' + operator + ' available'
            if not calls_waiting_queue.empty():
                 disenqueued_call_id = calls_waiting_queue.get()
                 ring(operator, disenqueued_call_id)
        else:
            for operator, respective_call in ringingCalls.iteritems():
                if respective_call == call:
                    del ringingCalls[operator]
                    print 'Call ' +  call + ' missed'
                    if not calls_waiting_queue.empty():
                        disenqueued_call_id = calls_waiting_queue.get()
                        ring(operator, disenqueued_call_id)
                    return
            if remove_from_queue(call):
                print 'Call ' + call + ' missed'

    def do_create_operator(self, arg):
        args=arg.split()
        Operators[args[0]]='available'

    def emptyline(self):
        pass

    def do_exit(self, arg):
        return True

    def do_EOF(self, arg):
        return True

    def default(self, arg):
        args=arg.split()[0]
        if(args=='#'):
            return
        print '*** Unknown syntax: ' + args


Operators = {}     # operator:state
ringingCalls = {}  # operator:call_id
ongoingCalls = {}  # call_id:operator

calls_waiting_queue = Queue.Queue()

Cmd=Cmd()
Cmd.prompt = ''
Cmd.cmdloop()
