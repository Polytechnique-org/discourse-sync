#!/usr/bin/env python3
# *-* coding: utf-8 *-*
from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError
from extract_Xnet_data import extract_all_groups, extract_groups_from_hruid
import yaml
import time

with open("config.yml") as conf_f:
    conf = yaml.load(conf_f)
    URL = conf['Discourse_API_URL']
    USERNAME = conf['Discourse_API_username']
    API_KEY = conf['Discourse_API_key']

client = DiscourseClient(URL, USERNAME, API_KEY)

def discourseName(netName):
    dName = netName
    if len(dName) < 3:
        #this name is too short for discourse, let's prepend _ to it
        dName = '_'*(3-len(dName)) + dName
    elif len(dName) > 20:
        #this name is too long for discourse, let's cut it
        dName = dName[:20]
    return dName

def getAllDiscourseMembers():
    all_discourse_members = {}
    for member in client.users():
        c = client.user_all(member['id']).get('single_sign_on_record', None)
        if c is not None:
            all_discourse_members[c['external_id']] = c['user_id']

    return all_discourse_members

def getAllDiscourseGroups():
    list_groups = client.groups()
    discourse_groups = {group['name'] : group for group in list_groups}
    return discourse_groups



def sync_all_groups():
    #Extract all X.net groups
    list_net_groups = extract_all_groups()

    #Extract all discourse members
    all_discourse_members = getAllDiscourseMembers()

    #Extract all discourse groups
    discourse_groups = getAllDiscourseGroups()

    #Sync each group
    adds = 0
    dels = 0
    for net_group_name in list_net_groups.keys():
        net_members = list_net_groups[net_group_name]
        d_group_name = discourseName(net_group_name)
        if d_group_name not in discourse_groups:
            [thisadd, thisdel] = sync_group(None, net_group_name, d_group_name, net_members, all_discourse_members)
        else:
            if discourse_groups[d_group_name].get('id') is None:
                print("Problem in group {0}.".format(net_group_name))
            else:
                [thisadd, thisdel] = sync_group(discourse_groups[d_group_name].get('id'), net_group_name, d_group_name, net_members, all_discourse_members)
        adds += thisadd
        dels += thisdel
    return adds, dels

def createGroup(name):
    print("Creating group '{0}'".format(name))
    return client.create_group(name, "").get('basic_group').get('id')

def sync_group(group_id, group_name, d_group_name, net_members, all_discourse_members):
    if group_id is None:
        old_members = []
    else:
        old_members = client.group_members(d_group_name)
    discourse_members = [member['id'] for member in old_members]
    l = []
    empty = True
    adds = 0
    dels = 0

    if net_members is not None:
        for member in net_members:
            if member in all_discourse_members:
                member_id = all_discourse_members[member]
                if member_id in discourse_members:
                    discourse_members.remove(member_id)
                    empty = False
                else:
                    if group_id is None:
                        group_id = createGroup(d_group_name)
                    member = client.add_user_to_group(group_id, member_id)
                    adds += 1
                    empty = False
                l.append(member_id)

        for member_id in discourse_members:
            client.delete_group_member(group_id, member_id)
            dels += 1

    if empty and group_id is not None:
        client.delete_group(group_id)
        print("Deleted empty group {0}.".format(group_name))
    return adds, dels

def sync_user(hruid):
    """
    Syncs all groups for a given user.
    Creates relevant groups if necessary

    Args:
        hruid: hruid in X.net of the user
    Returns:
		count_adds: the number of group additions for this user

    """
    net_groups = extract_groups_from_hruid(hruid)
    d_groups = getAllDiscourseGroups()
    user_data = client.user_by_external_id(hruid)
    uid = user_data['id']
    d_user_groups = {g['name']:g['id'] for g in user_data['groups']}
    count_adds = 0
    for net_group_name in net_groups:
        d_group_name = discourseName(net_group_name)
        if d_group_name in d_user_groups:
            continue
        if d_group_name in d_groups:
            group_id = d_groups[d_group_name]['id']
        else:
            group_id =  createGroup(d_group_name) 
        client.add_user_to_group(group_id, uid)
        count_adds += 1
    return count_adds

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true', help='Synchronize the whole database with Discourse')
    parser.add_argument('--user', help='Synchronize one user')
    parser.add_argument('--sleep', help='Adds a delay before acting')
    args = parser.parse_args()
    if args.sleep:
        time.sleep(int(args.sleep))
    if args.all:
        [adds, dels] = sync_all_groups()
        print('Sync performed {} group member additions and {} group member deletions'.format(adds,dels))
    else:
        if args.user:
            num = sync_user(args.user)
            print('User {} has been added to {} groups.'.format(args.user, num))
        else:
            from sys import exit,stderr
            print('Error: nothing to do. Please provide an user or use --all', file=stderr)
            exit(1)
