#!/usr/bin/env python3
# *-* coding: utf-8 *-*
import MySQLdb
import yaml

with open("config.yml") as conf_f:
    conf = yaml.load(conf_f)
    USERNAME = conf['MySQL_username']
    PASSWORD = conf['MySQL_password']
    DATABASE = conf['MySQL_database']


def extract_all_groups():
    db = MySQLdb.connect(host='localhost', user=USERNAME, passwd=PASSWORD, db=DATABASE)
    cursor = db.cursor()
    #Get list of Groups
    cursor.execute("SELECT id,diminutif FROM `groups`")
    db.commit()
    results = cursor.fetchall()
    groupNameFromId = {}
    for r in results:
        groupNameFromId[r[0]] = r[1]
    #Get members per group
    group_list = {}
    for (gid,gname) in groupNameFromId.items():
        cursor.execute("SELECT accounts.hruid FROM group_members INNER JOIN accounts ON accounts.uid = group_members.uid WHERE group_members.asso_id=%s", [gid]);
        db.commit()
        group_list[gname] = [x[0] for x in cursor.fetchall()]
    return group_list

def extract_groups_from_hruid(hruid):
    db = MySQLdb.connect(host='localhost', user=USERNAME, passwd=PASSWORD, db=DATABASE)
    cursor = db.cursor()
    #Get uid
    cursor.execute("SELECT uid FROM `accounts` WHERE `hruid` LIKE %s LIMIT 1", [hruid])
    db.commit()
    uid = int(cursor.fetchone()[0])
    #Get all groups
    cursor.execute("SELECT diminutif FROM `groups` INNER JOIN group_members ON groups.id=group_members.asso_id WHERE group_members.uid = %s", [uid])
    db.commit()
    data = cursor.fetchall()
    groups = [d[0] for d in data]
    return groups


if __name__ == '__main__':
    extract_all_groups()


