import sys
import os
from chef import autoconfigure, Node
import re

class ChefCommand:
    def fqdn_for_node(self,node):
        self.node = node
        api = autoconfigure()
        n = Node(node)
        if n:
            try:
                self.fqdn = n.attributes['ec2']['public_hostname']
            except KeyError:
                self.fqdn = n['fqdn']
        else:
            return None

        return self.fqdn

    def find_arg_idx(self):
        hostname_arg_idx = -1
        for i in range(len(sys.argv)):
            if self.is_node_arg(sys.argv[i]):
                hostname_arg_idx = i
        return hostname_arg_idx

    def run(self):
        idx = self.find_arg_idx()
        updated_arg = self.substitute_fdqn(sys.argv[idx])
        args = self.exec_args()
        for i in range(1,len(sys.argv)):
            if i != idx:
                args.append(sys.argv[i])
            else:
                args.append(updated_arg)

        args.extend(self.extra_args())

        print "Connecting to %s" % (self.fqdn)
        os.execvp(args[0],args)

    def is_node_arg(self,arg):
        return False

    def exec_args(self):
        """ Template method to return the first arg(s) to pass to execvp """
        return None

    def extra_args(self):
        """ Template method to allow subclasses to append additional arguments """
        return []

    def substitute_fdqn(self,arg):
        """ Template method for subclasses to override """
        return arg



class SshChefCommand(ChefCommand):
    # Borrowed with homage from ec2-ssh
    SSH_CMD='echo ". ~/.bashrc && PS1=\'\[\033[01;32m\]%s\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ \'" > ~/.ec2sshrc; /bin/bash --rcfile .ec2sshrc -i'

    def find_arg_idx(self):
        return len(sys.argv) - 1

    def extra_args(self):
        return [self.SSH_CMD % self.node]

    def exec_args(self):
        return ['ssh','-t']

    def substitute_fdqn(self,arg):
        m = re.match("(.*)@(.*)",arg)
        if m:
            username = m.group(1)
            node = m.group(2)
            return "%s@%s" % (username,self.fqdn_for_node(node))
        return self.fqdn_for_node(arg)


class ScpChefCommand(ChefCommand):
    def is_node_arg(self,arg):
        return arg.find(":") > 0

    def exec_args(self):
        return ["scp"]

    def substitute_fdqn(self,arg):
        (user_at_host,path) = arg.split(":")
        m = re.match("(.*)@(.*)",user_at_host)
        if m:
            username = m.group(1)
            node = m.group(2)
            return "%s@%s:%s" % (username,self.fqdn_for_node(node),path)
        return "%s:%s" % (self.fqdn_for_node(user_at_host),path)


def scp():
    scp_command = ScpChefCommand()
    scp_command.run()

def ssh():
    ssh_command = SshChefCommand()
    ssh_command.run()

if __name__ == "__main__":
    ssh()