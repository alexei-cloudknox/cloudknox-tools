# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import psycopg2

common_db_name = "db_common"
entitlements_db_name = "db_entitlements"
activities_db_name = "db_activities"
consumable_data_db_name = "db_consumable_data"

def convert_tuple(tup):
    st = ' '.join(map(str, tup))
    return st


def print_records(msg, records, pf):
    if len(records) == 0:
        return
    print("{}{}".format(pf, msg))
    for r in records:
        print("{}\t{}".format(pf, convert_tuple(r)))


def get_org_data(p_config):
    config = p_config.get("postgres_li")
    org_id = p_config.get("org_id")
    auth_id = p_config.get("auth_system_id")
    with psycopg2 \
            .connect("host={} port={} dbname={} user={} password={}"
                             .format(config.get("host"), config.get("port"), common_db_name, config.get("user"),
                                     config.get("password"))) \
        as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT shard_id FROM org_shard_mapping WHERE organization_id='{}'".format(org_id))
            records = cur.fetchall()
            if (len(records) != 1):
                print("Number of records in shard table for org/authSystem must be 1. Got: {}".format(len(records)))
                exit(1)
            shard_id = records[0][0]

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM data_sources WHERE organization_id='{}' and auth_system_id='{}'".format(org_id, auth_id))
            records = cur.fetchall()
            if (len(records) != 1):
                print("Number of records in data_source table for org/authSystem must be 1. Got: {}".format(len(records)))
                exit(1)
            data_source_id = records[0][0]
        return data_source_id, shard_id


def get_identity_info(conn, data_source_id, shard_id, user_name, pf):
    with conn.cursor() as cur:
        statement = "SELECT * FROM identities_{} WHERE data_source_id={} and identity_type=1 and identity_name='{}'"\
                                 .format(shard_id, data_source_id, user_name)
        cur.execute(statement)
        records = cur.fetchall()
        if len(records) > 0:
            print_records("Identity records", records, pf)
            if (len(records) != 1):
                print("Number of records in identities table for user {} must be 1. Got: {}".format(user_name, len(records)))
                exit(1)
            else:
                return records[0][0], records[0][2] # return ref id and identity_id
    with conn.cursor() as cur:
        statement = "SELECT * FROM identities_transient_{} WHERE data_source_id={} and identity_type=1 and identity_name='{}'"\
                                 .format(shard_id, data_source_id, user_name)
        cur.execute(statement)
        records = cur.fetchall()
        if len(records) > 0:
            print_records("Transient Identity records", records, pf)
            if (len(records) != 1):
                print("Number of records in identities table for user {} must be 1. Got: {}".format(user_name, len(records)))
                exit(1)
            else:
                return records[0][0], records[0][2]  # return ref id and identity_id
        else:
            raise Exception("No identity {} found.".format(user_name))

def print_grant_summary(conn, data_source_id, shard_id, ref_id, pf):
    with conn.cursor() as cur:
        fields = "num_tasks_granted, num_high_risk_tasks_granted, num_delete_tasks_granted, num_resources_granted, num_memberships, num_permissions"
        statement = "SELECT {} FROM identity_grants_summary_{} WHERE data_source_id={} and identity_ref_id={}"\
                   .format(fields, shard_id, data_source_id, ref_id)
        cur.execute(statement)
        record = cur.fetchall()
        if len(record) > 0:
            fld_data_list = []
            split_fls = fields.split(', ')
            for index in range(len(split_fls)):
                fld_data_list.append("{}: {}, ".format(split_fls[index], record[0][index]))
            print_records("Grants Summary:", [fld_data_list], pf)


def print_permissions_summary(conn, data_source_id, shard_id, ref_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT permission_id FROM identity_permissions_{} WHERE data_source_id={} and identity_ref_id={}"\
                                 .format(shard_id, data_source_id, ref_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}\tTotal number of granted permissions: {}".format(pf, len(records)))


def print_events(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT id FROM events_{} WHERE data_source_id={} and identity_id='{}'" \
            .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of events performed by identity: {}".format(pf, len(records)))


def print_accessed_identities_summary(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT id FROM identities_accessed_{} WHERE data_source_id={} and (source_identity_id='{}' or target_identity_id='{}')"\
                                 .format(shard_id, data_source_id, ident_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of accesses with identity id: {}".format(pf, len(records)))


def print_identity_login_summary(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT id FROM identity_logins_{} WHERE data_source_id={} and identity_id='{}'"\
                                 .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of logins by identity id: {}".format(pf, len(records)))


def print_identity_tasks_summary(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT id FROM identity_tasks_{} WHERE data_source_id={} and identity_id='{}'"\
                                 .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of tasks by identity id: {}".format(pf, len(records)))


def print_session_tokens_summary(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT id FROM session_tokens_{} WHERE data_source_id={} and identity_id='{}'"\
                                 .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of session tokens by identity id: {}".format(pf, len(records)))


def print_access_key_usage(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        fields = "identity_name, num_tasks_granted, num_tasks_used, num_high_risk_tasks_granted, num_high_risk_tasks_used, num_delete_tasks_granted, num_delete_tasks_used, num_resources_granted"
        statement = "SELECT {} FROM accesskey_entitlements_usage_summary_{} WHERE data_source_id={} and owner_id='{}'"\
                                 .format(fields, shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        if len(records) > 0:
            records_data = []
            for record in records:
                fld_data_list = []
                split_fls = fields.split(', ')
                for index in range(len(split_fls)):
                    fld_data_list.append("{}: {}, ".format(split_fls[index], record[index]))
                records_data.append(fld_data_list)
            print_records("Access Key Usages:", records_data, pf)


def print_auto_pilot_recommendations_0(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT id FROM auto_pilot_recommendations_{} WHERE data_source_id={} and identity_id='{}'"\
                                 .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of autopilot recommendations with identity id: {}".format(pf, len(records)))

def print_identity_access_advisor_tasks(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT service FROM identity_access_advisor_tasks_{} WHERE data_source_id={} and identity_id='{}'" \
            .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of services with advisor tasks with identity id: {}".format(pf, len(records)))


def print_identity_entitlements_usage_summary(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        fields = "pci_score, num_tasks_granted, num_tasks_used, num_high_risk_tasks_granted, num_high_risk_tasks_used, num_delete_tasks_granted, num_delete_tasks_used, num_resources_granted"
        statement = "SELECT {} FROM identity_entitlements_usage_summary_{} WHERE data_source_id={} and identity_id='{}'" \
            .format(fields, shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        if len(records) > 0:
            records_data = []
            for record in records:
                fld_data_list = []
                split_fls = fields.split(', ')
                for index in range(len(split_fls)):
                    fld_data_list.append("{}: {}, ".format(split_fls[index], record[index]))
                records_data.append(fld_data_list)
            print_records("Entitlements Usage:", records_data, pf)


def print_identity_risk_score(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT category FROM identity_risk_score_{} WHERE data_source_id={} and identity_id='{}'" \
            .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of risk scores categories with identity id: {}".format(pf, len(records)))


def print_identity_task_usage(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT used_tasks_bitmask FROM identity_task_usage_{} WHERE data_source_id={} and identity_id='{}'" \
            .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of task usages for identity id: {}".format(pf, len(records)))


def print_privilege_escalation(conn, data_source_id, shard_id, ident_id, pf):
    with conn.cursor() as cur:
        statement = "SELECT rule FROM privilege_escalation_{} WHERE data_source_id={} and identity_id='{}'" \
            .format(shard_id, data_source_id, ident_id)
        cur.execute(statement)
        records = cur.fetchall()
        print("{}Total number of privilege escalations for identity id: {}".format(pf, len(records)))


def collect_pgs_info(p_config, pf):
    config_li = p_config.get("postgres_li")
    (data_source_id, shard_id) = get_org_data(p_config)
    print("{}From Entitlements DB:".format(pf))
    with psycopg2 \
            .connect("host={} port={} dbname={} user={} password={}"
                             .format(config_li.get("host"),  config_li.get("port"), entitlements_db_name, config_li.get("user"),
                                     config_li.get("password"))) \
            as conn:
        (ref_id, ident_id) = get_identity_info(conn, data_source_id, shard_id, p_config.get("user_name"), pf+pf)
        p_config["user_ref_id"] = ref_id
        p_config["user_ident_id"] = ident_id
        print_grant_summary(conn, data_source_id, shard_id, ref_id, pf+pf)
        print_permissions_summary(conn, data_source_id, shard_id, ref_id, pf+pf)

    print("{}From Activities DB:".format(pf))
    config_hi = p_config.get("postgres_hi")
    with psycopg2 \
            .connect("host={} port={} dbname={} user={} password={}"
                             .format(config_hi.get("host"),  config_hi.get("port"), activities_db_name, config_hi.get("user"),
                                     config_hi.get("password"))) \
            as conn:
        print_events(conn, data_source_id, shard_id, ident_id, pf+pf)
        print_accessed_identities_summary(conn, data_source_id, shard_id, ident_id, pf+pf)
        print_identity_login_summary(conn, data_source_id, shard_id, ident_id, pf+pf)
        print_identity_tasks_summary(conn, data_source_id, shard_id, ident_id, pf+pf)
        print_session_tokens_summary(conn, data_source_id, shard_id, ident_id, pf+pf)

    print("{}From Consumable Data DB:".format(pf))
    with psycopg2 \
            .connect("host={} port={} dbname={} user={} password={}"
                             .format(config_li.get("host"), config_li.get("port"),consumable_data_db_name, config_li.get("user"),
                                     config_li.get("password"))) \
            as conn:
        print_access_key_usage(conn, data_source_id, shard_id, ref_id, pf+pf)
        print_auto_pilot_recommendations_0(conn, data_source_id, shard_id, ref_id, pf+pf)
        print_identity_access_advisor_tasks(conn, data_source_id, shard_id, ident_id, pf+pf)
        print_identity_entitlements_usage_summary(conn, data_source_id, shard_id, ref_id, pf+pf)
        print_identity_risk_score(conn, data_source_id, shard_id, ref_id, pf+pf)
        print_identity_task_usage(conn, data_source_id, shard_id, ref_id, pf+pf)
        print_privilege_escalation(conn, data_source_id, shard_id, ref_id, pf+pf)