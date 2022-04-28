# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json

import mysql.connector as mysql
import trino
from trino.auth import CertificateAuthentication, BasicAuthentication


def get_datalake_data(p_config):
    config = p_config.get("data_lake")
    with trino.dbapi. \
            connect(
                  http_scheme="http",
                  user=config.get("user"),
                  #auth=CertificateAuthentication("cert.pem", "key.pem"),
                  #auth=BasicAuthentication(config.get("user"), config.get("password")),
                  host=config.get("host"),
                  port=config.get("port"),
                  catalog=config.get("db")
           ) \
        as conn:
                cur = conn.cursor()
        # hourly_anomaly_alerts, statistical_alerts, par_alerts, activity_alerts
            #with conn.cursor() as cur:
                cur.execute("SELECT * FROM activity_alerts")
                data = cur.fetchall()
                if data:
                    print('Version retrieved: ', data)
                else:
                    print('Version not retrieved.')
