

class Op(object):
    pass

class AddMachine(Op):
    pass

class RemoveMachine(Op):
    pass

class 



class StreamHandler(Op):

    def add_machine(self, machine, spec):
        self.client.add_machine(machine, spec)

    def remove_machine(self, machine):
        self.client.remove_machine(machine)

    def add_unit(self, service_name, spec, number):
