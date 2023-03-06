#!/usr/bin/env python
try:
    import sys, random, os, time, datetime, json
    from datetime import timedelta
    from libs.isbusiness_time import _isbusiness_time as isbt
    from pyrfc import Connection, get_nwrfclib_version
    from libs.horus_utils import horus_root
    from libs.manage_credentials import _check_credentials, _get_credentials
except ImportError as e:
    print('Module with problems: {0}'.format(e))

horus_root = horus_root()

# get argv and convert to to dict
raw_argv = sys.argv[1]
fd = eval(raw_argv)


# define variables
fqdn=fd['fqdn']
sap_sid=fd['sap_sid']
sap_client=fd['sap_client']
sap_sysn=fd['sap_sysn']
product_type=fd['product_type']
environment=fd['environment']
isbt_start=fd['isbusiness_time']['start']
isbt_end=fd['isbusiness_time']['end']
project=fd['project']
instance_type=fd['instance_type']
instance_id=fd['instance_id']
environment_status=fd['environment_status']


# Checks before execution
if isbt(isbt_start,isbt_end) != True: quit()
if _check_credentials(instance_id,'abap') != True: quit()


try:
    urls=fd['urls']
except:
    print('Not urls to check, continue...')

# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']

# write to influx
def write_result(wp_dia_total, wp_dia_running, wp_upd_total, wp_upd_running, wp_bgd_total, wp_bgd_running, wp_spo_total, wp_spo_running):
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
    Point("monitoring")
    .tag("environment_status", environment_status)    
    .tag("instance_id", instance_id)
    .tag("instance_type", instance_type)    
    .tag("project", project)    
    .tag("fqdn", fqdn)
    .tag("sap_sid", sap_sid)
    .tag("sap_client", sap_client)
    .tag("sap_sysn", sap_sysn)
    .tag("product_type", product_type)
    .tag("environment", environment)
    .tag("sap_wp_info", "sap_wp_info")
    .field("wp_dia_total", wp_dia_total)
    .field("wp_dia_running", wp_dia_running)
    .field("wp_upd_total", wp_upd_total)
    .field("wp_upd_running", wp_upd_running)
    .field("wp_bgd_total", wp_bgd_total)
    .field("wp_bgd_running", wp_bgd_running)
    .field("wp_spo_total", wp_spo_total)
    .field("wp_spo_running", wp_spo_running)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)


def _getwpinfo():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : _get_credentials(instance_id,'ABAP')['username'],
        'passwd' : _get_credentials(instance_id,'ABAP')['password'],
    }

    try:
        conn = Connection(**conn_params)

        wpinfo=conn.call("EW_TH_WPINFO")
        info=wpinfo['WPLIST']
        totalprocesses=(len(info))

        wp_dia_total = 0
        wp_dia_running = 0
        for data in info:
            if data['WP_TYP'] == 'DIA': 
                wp_dia_total += 1
                if data['WP_STATUS'] == 'Running': wp_dia_running += 1

        wp_upd_total = 0
        wp_upd_running = 0
        for data in info:
            if data['WP_TYP'] == 'UPD': 
                wp_upd_total += 1
                if data['WP_STATUS'] == 'Running': wp_upd_running += 1

        wp_bgd_total = 0
        wp_bgd_running = 0
        for data in info:
            if data['WP_TYP'] == 'BGD': 
                wp_bgd_total += 1
                if data['WP_STATUS'] == 'Running': wp_bgd_running += 1

        wp_spo_total = 0
        wp_spo_running = 0
        for data in info:
            if data['WP_TYP'] == 'SPO': 
                wp_spo_total += 1
                if data['WP_STATUS'] == 'Running': wp_spo_running += 1

        write_result(wp_dia_total, wp_dia_running, wp_upd_total, wp_upd_running, wp_bgd_total, wp_bgd_running, wp_spo_total, wp_spo_running)
        
        conn.close()
    except:
        print('Something was wrong...')

_getwpinfo()