#!/usr/bin/env python3
# *-* coding: utf-8 *-*
from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError
from extract_Xnet_data import extract
import yaml

with open("config.yml") as conf_f:
    conf = yaml.load(conf_f)
    URL = conf['Discourse_API_URL']
    USERNAME = conf['Discourse_API_username']
    API_KEY = conf['Discourse_API_key']

client = DiscourseClient(URL, USERNAME, API_KEY)
list_net_groups = extract()
all_discourse_members = {}

for member in client.users():
    c = client.user_all(member['id']).get('single_sign_on_record', None)
    if c is not None:
        all_discourse_members[c.get('external_id')] = c.get('id')

def main():
    list_groups = client.groups()
    discourse_groups = {group['name'] : group for group in list_groups}

    for net_group_name in list_net_groups.keys():
        d_group_name = net_group_name
        if len(d_group_name) < 3:
            #this name is too short for discourse, let's prepend _ to it
            d_group_name = '_'*(len(d_group_name)-3) + d_group_name
        elif len(d_group_name) > 20:
            #this name is too long for discourse, let's cut it
            d_group_name = net_group_name[:20]
        if discourse_groups.get(d_group_name, None) is None:
            sync_group(None, net_group_name, d_group_name)
        else:
            if discourse_groups[d_group_name].get('id') is None:
                print("Problem in group {0}.".format(net_group_name))
            else:
                sync_group(discourse_groups[d_group_name].get('id'), net_group_name, d_group_name)

def sync_group(group_id, group_name, d_group_name):
    if group_id is None:
        old_members = []
    else:
        old_members = client.group_members(d_group_name)
    discourse_members = [member['id'] for member in old_members]
    net_members = list_net_groups[group_name]
    l = []
    empty = True

    if net_members is not None:
        for member in net_members:
            if member in all_discourse_members:
                member_id = all_discourse_members[member]
                if member_id in discourse_members:
                    discourse_members.remove(member_id)
                    empty = False
                else:
                    if group_id is None:
                        group_id = client.create_group(d_group_name, "").get('basic_group').get('id')
                        print("Created group '{0}'".format(group_name))
                    member = client.add_user_to_group(group_id, member_id)
                    empty = False
                l.append(member_id)

        for member_id in discourse_members:
            client.delete_group_member(group_id, member_id)

    if empty and group_id is not None:
        client.delete_group(group_id)
        print("Deleted empty group {0}.".format(group_name))

if __name__ == "__main__":
    main()
