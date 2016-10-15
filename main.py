from pydiscourse import DiscourseClient

URL = "https://forum.polytechnique.org"
USERNAME = ""
API_KEY = ""

def main():
    client = DiscourseClient(URL, USERNAME, API_KEY)

    # get list of .net groups
    lis_net_groups = []
    list_groups = client.groups()

    for group in list_net_groups:
        if group not in list_groups:
            client.create_group(group.name, group.title, visible)
            # get group_id
            sync_group(group_id, client)
        else:
            sync_group(group.id, client)

def sync_group(group_id, client):
    old_members = []
    # old_members =  group_id members
    # net_members = get_list_ne_members()
    # l = []
    for member in net_members:
        if member in old_members:
            del old_members[member]
        else:
            client.add_member_to_group(group_id, member.username)
        l.push(member)
    for member in old_members:
        client.delete_group_member(group_id, member.id)
