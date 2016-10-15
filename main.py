from pydiscourse import DiscourseClient

URL = "https://forum.polytechnique.org"
USERNAME = ""
API_KEY = ""

def main():
    client = DiscourseClient(URL, USERNAME, API_KEY)

    # get list of .net groups

    # if group does not exist
        # create it
        # get group_id
        # sync_group(group_id)
    # if group already exists
        # get group_id
        # sync_group(group_id)

def sync_group(group_id):
    # old_l =  group_id members
    # l = []
    # for each member of the .net group
        # if !old_l.contains(member)
            # client.add_member_to_group(group_id, username)
        # else 
            # old_l.delete(member)
        # l.push(member)
    # for member in old_l:
        # client.delete_group_member(group_id, user_id)

