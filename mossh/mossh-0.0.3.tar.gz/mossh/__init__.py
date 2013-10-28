#!/usr/bin/env python

import argparse
import subprocess
import os
import sys
import chef
import logging

SSH_PROCESS = "ssh"
CSSHX_PROCESS = "csshx"
WARN_LIMIT = 30

YES="y"
NO = "n"

class MosshException(Exception):
    pass

class NoNodesFoundError(MosshException):
    pass

class UnknownAttributeError(MosshException):
    pass

class ChefServerNotFoundError(MosshException):
    pass

def _ensure_csshx():
    try:
        result = subprocess.call([CSSHX_PROCESS,"--version"])
    except OSError:
        logging.error("You must have csshx installed to do multi-node queries")
        sys.exit()

def _get_chef_nodes_from_query(query,environment,num,offset,api):
    node_query = chef.Node(query,api=api)
    if node_query.exists:
        nodes = [node_query]
    else:
        nodes =[n.object for n in chef.Search("node",
                                              q="roles:%s AND chef_environment:%s" % (query,environment),
                                              rows=num,
                                              start=offset,
                                              api=api)]
        
    if not nodes:
        raise NoNodesFoundError
    return nodes

def main(args,api):
    if not api:
        raise ChefServerNotFoundError

    num = args.num if not args.all else 1000
    offset = args.offset if not args.all else 0

    nodes = []
    for query in args.query:
        nodes += _get_chef_nodes_from_query(query,args.environment,num,offset,api)
        num = max(num-len(nodes),0)
        offset = max(offset-len(nodes),0)
        
        if num == 0:
            break
        
    nodes_ips = set([node.attributes.get_dotted(args.a) for node in nodes if node.attributes.has_dotted(args.a)])
    missing_nodes_names = set([node.name for node in nodes if not node.attributes.has_dotted(args.a)])

    if not nodes_ips:
        raise UnknownAttributeError

    if missing_nodes_names:
        print logging.warning("Unable to log into following nodes because they do not have attribute %s:\%sn" % (args.a,", ".join(missing_node_names)))

    if len(nodes_ips) > WARN_LIMIT:
        human_response = raw_input("You are about to login to %s nodes. Are you sure you want to do this? (y/n): " % len(nodes_ips))
        while human_response not in [YES,NO]:
            human_response = raw_input("Bad Response. Try again (y/n): ")

        if human_response == NO:
            sys.exit()

    if len(nodes_ips) > 1:
        _ensure_csshx()


    client_process = SSH_PROCESS if len(nodes_ips) == 1 else CSSHX_PROCESS
    command_args = ["%s@%s" % (args.user,ipaddress) for ipaddress in nodes_ips]
    additional_args = []
    if args.forwardagent:
        if client_process == SSH_PROCESS:
            additional_args+=["-A"]
        elif client_process == CSSHX_PROCESS:
            additional_args+= ["--ssh_args","-A"]

    command_args+=additional_args

    print "Joining %s" %  " ".join(command_args)
    os.execvp(client_process,["hello world"] + command_args)
    

def run():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("query",type=str,nargs="+",help='Server role to ssh into')
    arg_parser.add_argument("--num",type=int,default=1,help='Number of servers to ssh into')
    arg_parser.add_argument("--offset",type=int,default=0,help='Offset servers')
    arg_parser.add_argument("--all",action="store_true",default=False,help='Number of servers to ssh into')
    arg_parser.add_argument("--environment",type=str,default="production",help='Server Environment')
    arg_parser.add_argument("--user",type=str,default="ubuntu",help='SSH user')
    arg_parser.add_argument("-a",type=str,default="ipaddress",help='Server Environment')
    arg_parser.add_argument("-A","--forwardagent",action="store_true",default=False,help='Forward your ssh agent')
    args = arg_parser.parse_args()

    main(args,api=chef.autoconfigure())
        
