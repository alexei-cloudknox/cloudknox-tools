# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json

import mysql.connector as mysql



class UserProperties:


    is_org_owner = False
    uid = None
    obf_data = {"name": "DELETED", "lname": "DELETED", "fname": "DELETED",
                "email": "DELETED@user.gdpr", "principal": "DELETED@user.gdpr",
                "display_name": "DELETED_USER_GDPR"}
    ctl_request_list = []
    report_schd_list = []
    sqs_notified = False
    email_notified = False

    def __init__(self, name, email, principal, obf_data):


        self.name = name
        self.email = email
        self.principal = principal
        self.obf_data = obf_data

    def set_user_id(self, user_id):
        self.uid = user_id

    def get_user_id(self):
        return self.uid

    def set_org_owner(self, is_owner):
        self.is_org_owner = is_owner

    def append_ctl_requests_list(self, req):
        self.ctl_request_list.append(req)

    def get_ctl_requests_list(self):
        return self.ctl_request_list

    def set_sqs_notified(self):
        self.sqs_notified = True

    def get_sqs_notified(self):
        return self.sqs_notified

    def set_email_notified(self):
        self.email_notified = True

    def get_email_notified(self):
        return self.email_notified

    def append_report_schd_list(self, req):
        self.report_schd_list.append(req)

    def get_report_schd_list(self):
        return self.report_schd_list

    def get_obf_name(self):
        return self.obf_data.get("name")

    def get_obf_lname(self):
        return self.obf_data.get("lname")

    def get_obf_fname(self):
        return self.obf_data.get("fname")

    def get_obf_dname(self):
        return self.obf_data.get("display_name")

    def get_obf_email(self):
        return self.obf_data.get("email")

    def get_obf_principal(self):
        return self.obf_data.get("principal")

def get_user_id(db, user, pf):
    with db.cursor() as cur:
        stat = "SELECT * FROM users WHERE "
        if user.principal is not None:
            stat += " user_principal_name = '{}'".format(user.principal)
        else:
            if user.email is not None:
                stat += " contact_email = '{}' or contact_emails_alternate = '{}' or contact_email_preferred = '{}'"\
                    .format(user.email, user.email, user.email)
            else:
                if user.name is not None:
                    un_split = user.name.split(' ')
                    if len(un_split) > 1:
                        stat += " (first_name = '{}' and last_name = '{}')".format(un_split[0], un_split[1])
                    else:
                        stat += " first_name = '{}'".format(user.name)
                else:
                    raise Exception("Can not make user selection. Principal name, email or user name should be defined.")
        print(stat)
        cur.execute(stat)
        data_list = list(cur.fetchall())
        if len(data_list) != 1:
            if len(data_list) > 1:
                for d in data_list:
                    print('{}row: {}'.format(pf, d))
                raise Exception("None or Multiple entries for the name {}. Set user_principal_name in the config file.".format(user.name))
            else:
                return user
        else:
            print("{}Found user record: \n\t{}{}".format(pf, pf, data_list[0]))
            user.set_user_id(data_list[0][0])
            return user


def check_if_org_creator(db, user, pf="\t"):
    with db.cursor() as cur:
        stat = "SELECT * FROM organizations WHERE created_by_user_id = '{}' ".format(user.uid)
        cur.execute(stat)
        data = list(cur.fetchall())
        if len(data) != 0:
            user.set_org_owner(True)
            print("{}User created following orgs:".format(pf))
            for d in data:
                print('\t{}{}'.format(pf, d))
        else:
            print("{}User is not owner of any orgs.".format(pf))


def check_if_notified_by_sqs(db, user, pf="\t"):
    if user.email is None:
        return
    with db.cursor() as cur:
        stat = "SELECT * FROM sqs_notifications WHERE recipient_email = '{}' ".format(user.email)
        cur.execute(stat)
        data = list(cur.fetchall())
        if len(data) != 0:
            user.set_sqs_notified()
            print("{}User SQS notified.".format(pf))
        else:
            print("{}User is not notified by sqs.".format(pf))


def check_if_registers_for_email_notification(db, user, pf="\t"):
    if user.email is None:
        return
    with db.cursor() as cur:
        stat = "SELECT * FROM notification_emails WHERE email = '{}' ".format(user.email)
        cur.execute(stat)
        data = list(cur.fetchall())
        if len(data) != 0:
            user.set_email_notified()
            print("{}User registered for email notifications.".format(pf))
        else:
            print("{}User is not registered for email notifications.".format(pf))


def check_if_listed_controller_request(db, config, user, pf="\t"):
    if user.email is None:
        return
    org_id = config.get("org_id")
    with db.cursor() as cur:
        stat = "SELECT identity_info, id FROM controller_requests WHERE organization_id = '{}'".format(org_id)
        cur.execute(stat)
        data = list(cur.fetchall())
        data_list = list(data)
        if len(data_list) != 0:
            for d in data_list:
                jobj = json.loads(d[0])
                if jobj.get("id") == user.email or jobj.get("email") == user.email:
                    user.append_ctl_requests_list((jobj, d[1]))
            if (len(user.get_ctl_requests_list()) > 0):
                print("{}User is listed in controller requests.".format(pf))
            else:
                print("{}User is not listed in controller requests.".format(pf))
        else:
            print("{}Organization is not listed in controller_requests table".format(pf))


def check_if_report_shared_with(db, config, user, pf="\t"):
    if user.email is None:
        return
    org_id = config.get("org_id")
    with db.cursor() as cur:
        stat = "SELECT share_with, id FROM report_schedule WHERE organization_id = '{}'".format(org_id)
        cur.execute(stat)
        data_list = list(cur.fetchall())
        if len(data_list) != 0:
            for d in data_list:
                jobj = json.loads(d[0])
                if user.email in jobj:
                    user.append_report_schd_list((jobj, d[1]))
            if len(user.get_report_schd_list()) > 0:
                print("{}User registered for report.".format(pf))
            else:
                print("{}User is not listed for reports.".format(pf))
        else:
            print("{}Organization is not listed in report_schedule table.".format(pf))


def print_user_info(p_config, pf):
    config = p_config.get("mysql_client")
    with mysql.\
            connect(
                host=config.get("host"),
                port=config.get("port"),
                user=config.get("user"),
                password=config.get("password"),
                database=config.get("db")) \
        as db:
        user = UserProperties(p_config.get("user_name"), p_config.get("user_email"),
                              p_config.get("user_principal_name"), p_config.get("obfuscation_data"))
        get_user_id(db, user, pf)
        check_if_org_creator(db, user, pf)
        check_if_notified_by_sqs(db, user, pf)
        check_if_registers_for_email_notification(db, user, pf)
        check_if_listed_controller_request(db, p_config, user, pf)
        check_if_report_shared_with(db, p_config, user, pf)
        return user


def remove_if_notified_by_sqs(db, config, user, pf="\t"):
    if not user.get_sqs_notified():
        print("{}No sqs notifications to delete".format(pf))
        return
    with db.cursor() as cur:
        stat = "DELETE FROM sqs_notifications WHERE recipient_email = '{}'".format(user.email)
        cur.execute(stat)
        print("{}Removed {} sqs notifications for user: {}".format(pf, cur.rowcount, user.email))
        return cur.rowcount


def remove_if_register_for_email_notification(db, config, user, pf="\t"):
    if not user.get_email_notified():
        print("{}No email notifications to delete".format(pf))
        return
    org_id = config.get("org_id")
    with db.cursor() as cur:
        stat = "DELETE FROM notification_emails WHERE organization_id {} AND email = '{}' ".format(org_id, user.email)
        cur.execute(stat)
        print("{}Removed {} email notifications for user: {}".format(pf, cur.rowcount, user.email))
        return cur.rowcount


def remove_if_listed_controller_request(db, config, user, pf="\t"):
    if len(user.get_ctl_requests_list()) == 0:
        print("{}No controller requests to update".format(pf))
        return
    with db.cursor() as cur:
        stat = "UPDATE controller_requests "
        updated = 0
        for (jobj, id) in user.get_ctl_requests_list():
            jobj["id"] = user.get_obf_email()
            jobj["name"] = user.get_obf_name()
            jobj["subType"] = "LOCAL"
            lstat = stat + "SET identity_info = '{}' WHERE id = '{}'".format(json.dumps(jobj), id)
            cur.execute(lstat)
            updated += 1
        print("{}Updated {} controller_requests for user: {}".format(pf, updated, user.email))
        return cur.rowcount


def remove_if_report_shared_with(db, config, user, pf="\t"):
    if len(user.get_report_schd_list()) == 0:
        print("{}No reports schedule to update".format(pf))
        return
    with db.cursor() as cur:
        update_stat = "UPDATE report_schedule SET "
        updated = 0
        for (jobj, id) in user.get_report_schd_list():
            jobj.remove(user.email)
            lstat = update_stat + "shared_with = '{}' WHERE id = '{}'".format(jobj.dump(), id)
            cur.execute(lstat)
            updated += 0
        print("{}Updated {} report_schedule for user: {}".format(pf, updated, user.email))


def obfuscate_user(db, user, pf):
    if user.get_user_id() is None:
        return
    with db.cursor() as cur:
        stat = "UPDATE users " \
               "SET first_name = '{}', last_name = '{}', display_name = '{}', " \
               "contact_email = '{}', contact_emails_alternate = '{}', " \
                "contact_email_preferred = '{}', user_principal_name = '{}', " \
               "status = 'DEACTIVATED' " \
               "WHERE id = '{}'".format(user.get_obf_fname(), user.get_obf_lname(), user.get_obf_dname(),
                                        "[]", "[]",
                                        user.get_obf_email(), user.get_obf_principal(),
                                        user.uid)
        cur.execute(stat)
        if cur.rowcount > 0:
            print("{}User is obfuscated in users table".format(pf))
        return cur.rowcount


def delete_user(db, user, pf):
    with db.cursor() as cur:
        stat = "DELETE FROM users WHERE id = '{}'".format(user.uid)
        cur.execute(stat)
        return cur.rowcount


def update_user_info(db, p_config, user, pf):
    return obfuscate_user(db, user, pf)


def delete_info(p_config, user, pf):
    config = p_config.get("mysql_client")
    with mysql.connect(
        host=config.get("host"),
        port=config.get("port"),
        user=config.get("user"),
        password=config.get("password"),
        database=config.get("db")) \
    as connection:
        remove_if_notified_by_sqs(connection, p_config, user, pf)
        remove_if_register_for_email_notification(connection, p_config, user, pf)
        remove_if_listed_controller_request(connection, p_config, user, pf)
        remove_if_report_shared_with(connection, p_config, user, pf)
        update_user_info(connection, p_config, user, pf)
        connection.commit()
