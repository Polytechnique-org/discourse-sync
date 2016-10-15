#!/usr/bin/env python3
# *-* coding: utf-8 *-*
import MySQLdb
import yaml

with open("config.yml") as conf_f:
    conf = yaml.load(conf_f)
    USERNAME = conf['MySQL_username']
    PASSWORD = conf['MySQL_password']
    DATABASE = conf['MySQL_database']


def extract():
    db = MySQLdb.connect(host='localhost', user=USERNAME, passwd=PASSWORD, db=DATABASE)
    cursor = db.cursor()
    #Get list of Groups
    cursor.execute("SELECT id,nom FROM `groups`")
    db.commit()
    results = cursor.fetchall()
    groupNameFromId = {}
    for r in results:
        groupNameFromId[r[0]] = r[1]
    #Get members per group
    group_list = {}
    for (gid,gname) in groupNameFromId.items():
        cursor.execute("SELECT accounts.hruid FROM group_members INNER JOIN accounts ON accounts.uid = group_members.uid WHERE group_members.asso_id=" + str(gid));
        db.commit()
        group_list[gname] = [x[0] for x in cursor.fetchall()]
    #Yaml everything and output it
    print(yaml.dump(group_list))
    return group_list

if __name__ == '__main__':
    extract()


