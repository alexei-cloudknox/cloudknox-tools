
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

class UserProperties:
    first_occurrence = -1
    last_occurrence = -1
    objects = None
    ent_type = None
    found_json = None
    minio_client = None

    def __init__(self, name, email, principal, org_id, auth_system_id, bucket):
        self.name = name
        self.email = email
        self.principal = principal
        self.org_id = org_id
        self.auth_system_id = auth_system_id
        self.bucket = bucket

    def is_found(self):
        return self.first_occurrence is not None \
               and self.last_occurrence is not None \
               and self.found_json is not None

    def set_ent_type(self, ent_type):
        self.ent_type = ent_type

    def set_found_first(self, json_user, obj_index):
        self.found_json = json_user
        self.first_occurrence = obj_index

    def print_info(self, pf):
        if self.found_json is not None:
            print("{}The first presents of {} in {}".format(pf, self.name, self.objects[self.first_occurrence].object_name))
            print("{}The last presents of {} in {}".format(pf, self.name, self.objects[self.last_occurrence].object_name))
            print("{}BackUp should be adjusted to keep only after last occurrence".format(pf))
        else:
            print("{}No objects found that contain user {}".format(pf, self.name))

    def init_minio_client(self, minio_conf):
        self.minio_client = \
            Minio(
                minio_conf.get("endpoint"),
                access_key=minio_conf.get("access_key"),
                secret_key=minio_conf.get("secret_key"),
                session_token=minio_conf.get("session_token"),
                secure=True if minio_conf.get("secure") is not None and minio_conf.get("secure") == True else False
            )

    def obtain_file_objects(self, ent_type, reset=False):
        if self.objects is not None and not reset:
            return
        path = "{}/{}/{}/".format(ent_type, self.org_id, self.auth_system_id)
        res_objects = self.minio_client.list_objects(self.bucket, prefix=path, recursive=True)
        self.objects = []
        for obj in res_objects:
            self.objects.append(obj)

    def check_ent_for_user(self, obj):
        ent_file_local = "/tmp/discover_file.json"
        ent_file_local_gz = "{}.gz".format(ent_file_local)
        try:
            data = self.minio_client.get_object(obj.bucket_name, obj.object_name)
            with open(ent_file_local_gz, 'wb') as file_data:
                for d in data.stream(32 * 1024):
                    file_data.write(d)
            process = subprocess.run(['gunzip', ent_file_local_gz], capture_output=True)
            if process.returncode != 0 and process.returncode != 2:
                raise Exception("Can not run gunzip on file {}".format(ent_file_local_gz))
            jobj = json.load(open(ent_file_local))
            ptrn = '.identities[] | select(.name == "{}" or .id == "{}" or .email == "{}")'.format(self.name, self.name, self.email)
            return pyjq.first(ptrn, jobj)
        except ResponseError as err:
            print(err)
            return None
        finally:
            if os.path.exists(ent_file_local):
                os.remove(ent_file_local)
            if os.path.exists(ent_file_local_gz):
                os.remove(ent_file_local_gz)

    def search_for_first_inclusion(self, from_ind, to_ind):
        if to_ind - from_ind <= 2:
            ind = from_ind
            json_user = self.check_ent_for_user(self.objects[from_ind])
            if json_user is None:
                ind = to_ind
                json_user = self.check_ent_for_user(self.objects[to_ind])
            self.set_found_first(json_user, ind)
            return json_user is not None
        mid = (from_ind + to_ind) // 2
        json_user = self.check_ent_for_user(self.objects[mid])
        if json_user is None:
            return self.search_for_first_inclusion(mid + 1, to_ind)
        else:
            return self.search_for_first_inclusion(from_ind, mid - 1)

    def find_first_object_with_user(self, ent_type):
        self.obtain_file_objects(ent_type)
        first_ent = self.objects[0]
        json_user = self.check_ent_for_user(first_ent)
        if json_user is None:
            self.search_for_first_inclusion(1, len(self.objects) - 1)
        else:
            self.first_occurrence = 0
            self.set_found_first(json_user, 0)
        if self.found_json is not None:
            self.set_ent_type(ent_type)
            return True
        else:
            return False

    def find_last_object_with_user(self):
        json_user = self.check_ent_for_user(self.objects[len(self.objects) - 1])
        if json_user is None:
            if self.first_occurrence == -1:
                raise Exception("First occurrence was not found. Run find_last_object_with_user prior.")
            return self.search_for_last_occurrence(self.first_occurrence, len(self.objects) - 2)
        self.last_occurrence = len(self.objects) - 1
        return True

    def search_for_last_occurrence(self, from_ind, to_ind):
        if to_ind - from_ind <= 2:
            ind = from_ind
            user = self.check_ent_for_user(self.objects[from_ind])
            if user is None:
                ind = to_ind
                user = self.check_ent_for_user(self.objects[to_ind])
            if user is not None:
                self.last_occurrence = ind
            return user is not None
        mid = (from_ind + to_ind) // 2
        user = self.check_ent_for_user(self.objects[mid])
        if user is None:
            return self.search_for_last_occurrence(from_ind, mid - 1)
        else:
            return self.search_for_last_occurrence(mid + 1, to_ind)

    def get_relevant_path(self):
        name = self.objects[self.last_occurrence].object_name
        sp_name = name.split('/')
        if len(sp_name) < 4:
            raise Exception("Path name should consist of more than 3 directories: {}".format(name))
        return "/".join(sp_name[1:len(sp_name) - 2])


def get_latest_for_obj_type(config, client, bucket, obj_type, depth):
    found = client.bucket_exists(bucket)
    if not found:
        raise Exception("{} bucket not found.".format(bucket))
    print("Getting objects from bucket {}".format(bucket))
    org_id = config.get("org_id")
    auth_system_id = config.get("auth_system_id")
    path = "{}/{}/{}/".format(obj_type, org_id, auth_system_id)
    objects = client.list_objects(bucket, prefix=path)
    depth_i = 0
    last_obj = None
    while depth_i < depth:
        for obj in list(objects):
            last_obj = obj
        if last_obj is None:
            raise Exception("ERROR: Path not found: {}/{}".format(bucket, path))
        objects = client.list_objects(bucket, prefix=last_obj.object_name)
        depth_i += 1
    return last_obj


def print_user_info(config, pf):
    minio_conf = config.get("minio_client")
    try:
        user = UserProperties(config.get("user_name"), config.get("user_email"),
                              config.get("user_principal_name"),
                              config.get("org_id"), config.get("auth_system_id"),
                              minio_conf.get("raw_bucket"))
        user.init_minio_client(minio_conf)
        collection_type = "entitlements"
        found = user.find_first_object_with_user(collection_type)
        if not found:
            try:
                collection_type = "samlidentities"
                found = user.find_first_object_with_user(collection_type)
            except Exception as e:
                print("Can not search for saml identities: {}".format(e))
        if not found:
            print("{}User {} not found in collected entitlements".format(pf, user.name))
            return 0
        user.find_last_object_with_user()
        user.print_info(pf)
        return user
    except Exception as e:
        print(e)
        return None


def delete_objects(user, collection_type, last_inclusion_path, pf):
    path = "{}/{}/{}/".format(collection_type, user.org_id, user.auth_system_id)
    res_objects = user.minio_client.list_objects(user.bucket, prefix=path, recursive=True)
    for obj in res_objects:
        sp_name = obj.object_name.split('/')
        if ",".join(sp_name[1:len(sp_name) - 2]) <= last_inclusion_path:
            print("{}Removing {}".format(pf, obj.object_name))
            user.minio_client.remove_object(user.bucket, obj.object_name)


def delete_info(config, user, pf):
    if user.is_found():
        relevant_path = user.get_relevant_path()
        print("{}Deleting all collection objects before {}".format(pf, relevant_path))
        delete_objects(user, user.ent_type, relevant_path, pf + pf)
        delete_objects(user, "tasks", relevant_path, pf + pf)

