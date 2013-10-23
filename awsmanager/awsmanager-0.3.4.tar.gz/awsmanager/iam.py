#!/usr/bin/python

import boto
from urllib2 import unquote

def print_all_policies():
    iam = boto.connect_iam()
    groups = iam.get_all_groups()['list_groups_response']['list_groups_result']['groups']
    for group in groups:
        policies = iam.get_all_group_policies(group_name=group['group_name'])
        for policy in policies['list_group_policies_response']['list_group_policies_result']['policy_names']:
            policy_res = iam.get_group_policy(group['group_name'], policy)

            policy_name = policy_res['get_group_policy_response']['get_group_policy_result']['policy_name']
            group_name = policy_res['get_group_policy_response']['get_group_policy_result']['group_name']
            document = unquote(policy_res['get_group_policy_response']['get_group_policy_result']['policy_document'])

            print "\n##### REMOVE ME ####: Name: [%s] of IAM group [%s]\n\n" % (policy_name, group_name)
            print document
            print "\n-----%<---- EOF ------%<-------- EOF --------------"
