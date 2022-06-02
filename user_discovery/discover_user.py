# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json

import datalake_discoverer
import mysql_discoverer
import pgs_discoverer
import s3_discoverer


def load_config(file_location):
    text_file = open(file_location, "r")
    data = text_file.read()
    text_file.close()
    return json.loads(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config-file', type=str,  default="discover_user_config.json",
                        help='Config file')
    parser.add_argument('--search-area', type=str, default='blob-storage,data-db,control-db,analytics-db',
                        help='Search areas. Any combinations of blob-storage,data-db,control-db,analytics-db. Default are all.')
    parser.add_argument('--delete', action='store_true',
                        help='Delete found info')
    args = parser.parse_args()
    config = load_config(args.config_file)
    search_area = set(args.search_area.split(','))
    pf = "\t"
    if 'data-db' in search_area:
        print("User Entitlements Data:")
        discovered_records = pgs_discoverer.print_user_info(config, pf)
        if discovered_records > 0 and args.delete is True:
            print("DELETING from User Entitlements Data:")
            pgs_discoverer.delete_info(config, pf)

    if 'control-db' in search_area:
        print("Data Access Control DB:")
        user = mysql_discoverer.print_user_info(config, pf)
        if user is not None and args.delete is True:
            print("DELETING from Data Access Control DB:")
            mysql_discoverer.delete_info(config, user, pf)

    if 'blob-storage' in search_area:
        print("User Raw Data and Backups:")
        user = s3_discoverer.print_user_info(config, pf)
        if user is not None and args.delete is True:
            print("DELETING from User Raw Data and Backups:")
            s3_discoverer.delete_info(config, user, pf)

    if 'analytics-db' in search_area:
        print("User DataLake Data:")
        discovered_records = datalake_discoverer.print_user_info(config, pf)
        if discovered_records > 0 and args.delete is True:
            print("DELETING from User DataLake Data:")
            datalake_discoverer.delete_info(config, pf)
