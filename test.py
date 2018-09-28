import cmd

class Cmd(cmd.Cmd):
    def do_foo(self, arg):
        print 'Hello World'
        
Cmd=Cmd()
Cmd.cmdloop('Welcome\nType h for help')