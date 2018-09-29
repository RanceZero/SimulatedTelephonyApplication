import cmd

class Cmd(cmd.Cmd):

    def do_call(self, arg):
        call_id = arg.split()[0]
        print 'Call ' + call_id + ' received'
        for operator, value in Operators.iteritems():
            if value == 'available':
                value = 'ringing'
                break
        ringingCalls[operator]=call_id
        print 'Call ' + call_id + ' ' + value +' for operator ' + operator


    def do_answer(self, arg):
        operator = arg.split()[0]
        call_id = ringingCalls[operator]
        Operators[operator]='busy'
        del ringingCalls[operator]
        print 'Call ' + call_id + ' answered by operator ' + operator

    def do_reject(self, arg):
        print 'Hello World'

    def do_hangup(self, arg):
        print 'Hello World'

    def do_create_operator(self, arg):
        args=arg.split()
        Operators[args[0]]='available'

    def emptyline(self):
        pass

    def do_exit(self, arg):
        return True

    def do_Test(self, arg):
        return

Operators = {}
ringingCalls = {}
ongoingCalls = {}

Cmd=Cmd()
Cmd.prompt = ''
Cmd.cmdloop()
