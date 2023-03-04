#!/usr/bin/env python
try:
    import sys, random, os, time, datetime, json
    from hdbcli import dbapi
    from datetime import timedelta
    import keyring
except ImportError as e:
    print('Module with problems: {0}'.format(e))

sap_sid='HLP'
product_type='hana'

# Read config File
with open("../ansible/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']

# write to influx
def write_result(ALERT_RATING,ALERT_NAME):
    try:
        import influxdb_client
        from influxdb_client import InfluxDBClient, Point, WritePrecision
        from influxdb_client.client.write_api import SYNCHRONOUS
    except ImportError as e:
        print('Module with problems: {0}'.format(e))

    client = influxdb_client.InfluxDBClient(url=influxdb_url, token=influx_token, org=influx_org, bucket_name=influx_bucket)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # alerts
    point = (
    Point("alerts")
    .tag("action", 'action')    
    .tag("instance_id", instance_id)
    .tag("instance_type", instance_type)    
    .tag("fqdn", '192.168.50.175')
    .tag("sap_sid", 'demo')
    .tag("sap_client", 'demo')
    .tag("sap_sysn", 'demo')
    .tag("hana_sid", 'demo')
    .tag("hana_sysn", 'demo')
    .tag("product_type", 'demo')
    .tag("environment", 'demo')
    .tag("hana", 'hana')
    .field("ALERT_NAME", ALERT_NAME)
    .field("ALERT_RATING", ALERT_RATING)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

def _sap_hana_alerts():
    conn = dbapi.connect(
        address="192.168.50.175", 
        port="39017", 
        user="SYSTEM", 
        password="Demo1234!"
    )

    cursor = conn.cursor()

    # Alerts:
    cursor.execute("SELECT ALERT_RATING,ALERT_NAME FROM _SYS_STATISTICS.STATISTICS_CURRENT_ALERTS")
    alerts = cursor.fetchall()
    try:
        for alert in alerts:
            ALERT_RATING=alert[0]
            ALERT_NAME=alert[1]
            write_result(ALERT_RATING,ALERT_NAME)    
    except:
        raise

_sap_hana_alerts()