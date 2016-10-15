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

list_net_groups = extract()

def main():
    client = DiscourseClient(URL, USERNAME, API_KEY)

    list_groups = client.groups()
    discourse_groups = {group['name'] : group for group in list_groups}

    for net_group_name in list_net_groups.keys():
        if len(net_group_name) < 3:
            print(str(net_group_name) + "'s name is too short for Discourse")
            continue
        if discourse_groups.get(net_group_name, None) is None:
            new_group = client.create_group(net_group_name, "")
            group_id = new_group.get('basic_group').get('id')
            sync_group(group_id, net_group_name, client)
        else:
            sync_group(discourse_groups[net_group_name].get('id'), net_group_name, client)

def sync_group(group_id, group_name, client):
    old_members = client.group_members(group_name)
    discourse_members = [member['id'] for member in old_members]
    net_members = list_net_groups[group_name]
    l = []

    if net_members is not None:
        for member in net_members:
            try:
                member_id = client.by_external_id(member)['id']
            except DiscourseClientError:
                member_id = 0
            if member_id != 0:
                if member_id in discourse_members:
                    discourse_members.remove(member_id)
                else:
                    member = client.add_user_to_group(group_id, member_id)
                l.append(member_id)

        for member_id in discourse_members:
            client.delete_group_member(group_id, member_id)

if __name__ == "__main__":
    main()
