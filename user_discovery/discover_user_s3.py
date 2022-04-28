# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import os
import subprocess
import zipfile
from xmlrpc.client import ResponseError

import pyjq
from minio import Minio


def check_ent_for_user(config, client, obj):
    user_name = config.get("user_name")
    ent_file_local = "/tmp/discover_file.json"
    ent_file_local_gz = "{}.gz".format(ent_file_local)
    try:
        data = client.get_object(obj.bucket_name, obj.object_name)
        with open(ent_file_local_gz, 'wb') as file_data:
            for d in data.stream(32 * 1024):
                file_data.write(d)
        process = subprocess.run(['gunzip', ent_file_local_gz], capture_output=True)
        if process.returncode != 0 and process.returncode != 2:
            raise Exception("Can not run gunzip on file {}".format(ent_file_local_gz))
        jobj = json.load(open(ent_file_local))
        ptrn = '.identities[] | select(.name == "{}" or .id == "{}")'.format(user_name, user_name)
        return pyjq.first(ptrn, jobj)
    except ResponseError as err:
        print(err)
        return None
    finally:
        if os.path.exists(ent_file_local):
            os.remove(ent_file_local)
        if os.path.exists(ent_file_local_gz):
            os.remove(ent_file_local_gz)


def get_latest_for_obj_type(config, client, obj_type, depth):
    bucket = config.get("raw_bucket")
    found = client.bucket_exists(bucket)
    if not found:
        raise Exception("{} bucket not found.".format(bucket))
    print("Getting objects from bucket {}".format(bucket))
    org_id = config.get("orgId")
    org_system_id = config.get("authSystemId")
    objects = client.list_objects(bucket, prefix="{}/{}/{}/".format(obj_type, org_id, org_system_id))
    depth_i = 0
    while depth_i < depth:
        for obj in list(objects):
            last_obj = obj
        objects = client.list_objects(bucket, prefix=last_obj.object_name)
        depth_i += 1
    return last_obj


def find_first_object_with_user(config, client, obj_type, pf):
    bucket = config.get("raw_bucket")
    org_id = config.get("orgId")
    org_system_id = config.get("authSystemId")
    path = "{}/{}/{}/".format(obj_type, org_id, org_system_id)
    res_objects = client.list_objects(bucket, prefix=path, recursive=True)
    objects = []
    for obj in res_objects:
        objects.append(obj)
    if len(objects) > 0:
        first_ent = objects[0]
        user = check_ent_for_user(config, client, first_ent)
        if user is None:
            user = search_for_first_inclusion(config, client, objects, 0, len(objects) - 1)
        if user is not None:
            print("{}First presents of {} in {}".format(pf, config.get("user_name"), objects[0].object_name))
        else:
            print("{}No objects found that contain user {}".format(pf, config.get("user_name")))
    else:
        print("{}No objects in the path: {}".format(pf, path))


def search_for_first_inclusion(config, client, objects, from_ind, to_ind):
    if to_ind - from_ind <= 2:
        user = check_ent_for_user(config, client, objects[from_ind])
        if user is None:
            user = check_ent_for_user(config, client, objects[to_ind])
        return user
    mid = (from_ind + to_ind) // 2
    user = check_ent_for_user(config, client, objects[mid])
    if user is None:
        return search_for_first_inclusion(config, client, objects, mid + 1, to_ind)
    else:
        return search_for_first_inclusion(config, client, objects, from_ind, mid - 1)



def list_data_from_raw_storage(config, pf):
    minio_conf = config.get("minio_client")
    print("https://{}:{}:{}@s3.amazonaws.com".format(minio_conf.get("access_key"), minio_conf.get("secret_key"), minio_conf.get("session_token")))
    client = Minio(
        minio_conf.get("endpoint"),
        access_key=minio_conf.get("access_key"),
        secret_key=minio_conf.get("secret_key"),
        session_token=minio_conf.get("session_token"),
        secure=True if minio_conf.get("secure") is not None and minio_conf.get("secure") == True else False
    )
    obj = get_latest_for_obj_type(config, client, "entitlements", 5)
    user = check_ent_for_user(config, client, obj)
    if user is None:
        obj = get_latest_for_obj_type(config, client, "samlidentities", 4)
        user = check_ent_for_user(config, client, obj)
    if user is None:
        print("{}User {} not found in entitlements".format(pf, config.get("user_name")))
        return 0
    else:
        print("{}User data in entitlements: {}".format(pf, user))


    print("{}First BackUp with User:".format(pf))
    find_first_object_with_user(config, client, "entitlements", pf+pf)
