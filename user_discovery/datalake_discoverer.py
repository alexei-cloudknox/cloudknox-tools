# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import trino

def get_identity_items_from_table(conn, config, table, pf):
    res = 0
    user_email = config.get("user_email")
    cur = conn.cursor()
    try:
        stat = "SELECT * FROM {} WHERE identity_id = '{}' LIMIT 101".format(table, user_email)
        cur.execute(stat)
        data = cur.fetchall()
        if data:
            res = len(data)
            print("{}Table {} Contains {} entries for user.".format(pf, table, res))
        else:
            print('{}Table does not contain any entries for user.'.format(pf, table))
    finally:
        cur.close()
    return res


def print_user_info(p_config, pf):
    config = p_config.get("data_lake")
    with trino.dbapi. \
            connect(
                  http_scheme="http",
                  user=config.get("user"),
                  #auth=CertificateAuthentication("cert.pem", "key.pem"),
                  #auth=BasicAuthentication(config.get("user"), config.get("password")),
                  host=config.get("host"),
                  port=config.get("port"),
                  catalog=config.get("catalog"),
                  schema=config.get("schema")
           ) \
        as conn:
        result = 0
        for table in ["tasks", "activity_alerts", "hourly_anomaly_alerts", "statistical_alerts", "par_alerts"]:
            print("{}Collecting from {}".format(pf, table))
            result += get_identity_items_from_table(conn, p_config, table, pf+pf)
        return result

def delete_identity_items_from_table(conn, config, table, pf):
    user_email = config.get("user_email")
    cur = conn.cursor()
    try:
        stat = "DELETE FROM {} WHERE identity_id = '{}'".format(table, user_email)
        cur.execute(stat)
        if cur.rowcount > 0:
            print("{}{} number of records deleted from {}.".format(pf, cur.rowcount, table))
        elif cur.rowcount == 0:
            print('{}Table does not contain any entries for user.'.format(pf, table))
        else:
            print("{}Unexpected result {} executing \"{}\".".format(pf, cur.rowcount, stat))
    finally:
        cur.close()


def delete_info(p_config, pf):
    config = p_config.get("data_lake")
    with trino.dbapi. \
            connect(
               http_scheme="http",
               user=config.get("user"),
               # auth=CertificateAuthentication("cert.pem", "key.pem"),
               # auth=BasicAuthentication(config.get("user"), config.get("password")),
               host=config.get("host"),
               port=config.get("port"),
               catalog=config.get("catalog"),
               schema=config.get("schema")
            ) \
            as conn:
            for table in ["tasks", "activity_alerts", "hourly_anomaly_alerts", "statistical_alerts", "par_alerts"]:
                print("{}Deleting from {}".format(pf, table))
                delete_identity_items_from_table(conn, p_config, table, pf + pf)
