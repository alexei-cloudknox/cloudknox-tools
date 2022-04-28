# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json

import mysql.connector as mysql

import discover_user_datalake
import discover_user_mysql
import discover_user_pgs
import discover_user_s3


def load_config(file_location):
    text_file = open(file_location, "r")
    data = text_file.read()
    text_file.close()
    return json.loads(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('config_file', type=str,
                        help='config file')
    args = parser.parse_args()
    config = load_config(args.config_file)

    print("Data Access Control DB:")
    #discover_user_mysql.get_mysql_data(config, "\t")
    print("User Entitlements Data:")
    discover_user_pgs.collect_pgs_info(config, "\t")
    print("User Raw Data and Backups:")
    #discover_user_s3.list_data_from_raw_storage(config, "\t")
    print("User DataLake Data:")
    discover_user_datalake.get_datalake_data(config)
