#!/usr/bin/env python
try:
    import sys, random, os, time, json, keyring
    from pyrfc import Connection, get_nwrfclib_version
    from libs.isbusiness_time import _isbusiness_time as isbt
    from libs.horus_utils import horus_root
    from libs.check_credentials import _check_credentials
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
action=fd['action']


# Checks before execution
if isbt(isbt_start,isbt_end) != True: quit()
if _check_credentials(instance_id,'abap') != True: quit()


# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']


# write to influx
def write_result(status):
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
    .tag("action", 'action')    
    .tag("instance_id", instance_id)
    .tag("instance_type", instance_type)    
    .tag("project", project)
    .tag("fqdn", fqdn)
    .tag("sap_sid", sap_sid)
    .tag("sap_client", sap_client)
    .tag("sap_sysn", sap_sysn)
    .tag("product_type", product_type)
    .tag("environment", environment)
    .field("abap_isup", status)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)
    quit()


def _sapabapisup():
    # pyrfc connection params
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : 'limbail',
        'passwd' : keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn, 'limbail'),
    }

    try:
        conn = Connection(**conn_params)
        if conn.alive == True:
            alive=True
            conn.close()
            print("server is up " + str(sap_sid) +" "+  str(fqdn))
            write_result(1)
        else: 
            print("server is down! " + str(sap_sid) +" "+  str(fqdn))
            write_result(0)

    except Exception as e:
        print("server is down! " + str(sap_sid) +" "+  str(fqdn))
        write_result(0)


if __name__ == '__main__':
    _sapabapisup()