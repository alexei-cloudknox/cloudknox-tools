# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json

import mysql.connector as mysql

def get_user_id(db, config, pf):
    with db.cursor() as cur:
        user_name = config.get("user_principal_name")
        if user_name is None:
            user_name = config.get("user_name")
            un_split = user_name.split(' ')
            if len(un_split) > 1:
                stat = "SELECT * FROM users WHERE first_name = '{}' and last_name = '{}'".format(un_split[0],
                                                                                                 un_split[1])
            else:
                stat = "SELECT * FROM users WHERE first_name = '{}'".format(user_name)
        else:
            stat = "SELECT * FROM users WHERE user_principal_name = '{}' ".format(user_name)
        cur.execute(stat)
        data = cur.fetchall()
        data_list = list(data)
        if len(data_list) != 1:
            for d in data_list:
                print('{}row: {}'.format(pf, d))
            raise Exception("None or Multiple entries for the name {}. Set user_principal_name in the config file.".format(user_name))
        else:
            print("{}Found user record: \n\t{}{}".format(pf, pf, data_list[0]))
            return data_list[0][0]


def check_if_org_creator(db, config, user_id, pf="\t"):
    with db.cursor() as cur:
        stat = "SELECT * FROM organizations WHERE created_by_user_id = '{}' ".format(user_id)
        cur.execute(stat)
        data = list(cur.fetchall())
        if len(data) != 0:
            print("{}User created following orgs:".format(pf))
            for d in data:
                print('\t{}{}'.format(pf, d))
        else:
            print("{}User is not owner of any orgs.".format(pf))


def get_mysql_data(p_config, pf):
    config = p_config.get("mysql_client")
    with mysql.\
            connect(
                host=config.get("host"),
                port=config.get("port"),
                user=config.get("user"),
                password=config.get("password"),
                database=config.get("db")) \
        as db:
        user_id = get_user_id(db, p_config, pf)
        check_if_org_creator(db, p_config, user_id, pf)