#!/usr/bin/env python
try:
    import sys, random, os, time, datetime, json, keyring
    from datetime import timedelta
    from libs.isbusiness_time import _isbusiness_time as isbt
    from pyrfc import Connection, get_nwrfclib_version
except ImportError as e:
    print('Module with problems: {0}'.format(e))

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


# we check business hour of hosts to decide if continue or not.
if isbt(isbt_start,isbt_end) != True: quit()


try:
    urls=fd['urls']
except:
    print('Not urls to check, continue...')

# Read config File
with open("myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']

# write to influx
def write_result(protocol,service,hostname):
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
    Point("security")
    .tag("fqdn", fqdn)
    .tag("sap_sid", sap_sid)
    .tag("sap_client", sap_client)
    .tag("sap_sysn", sap_sysn)
    .tag("product_type", product_type)
    .tag("environment", environment)
    .tag("hardening","hardening")
    .tag("icm_info","icm_info")
    .field('protocol', protocol)
    .field('service', service)
    .field('hostname', hostname)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

try:
    if keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'):
        print("Autorization was found, continue...")   
    else: quit()
except: 
    print('print("Not autorization was found")')
    quit()


def _sap_security_abap_protocolisup():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : 'limbail',
        'passwd' : keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'),
    }

    try:        
        conn = Connection(**conn_params)
        data = conn.call("ICM_GET_INFO")

        for i in data['SERVLIST']:
            protocol=i['PROTOCOL']
            service=i['SERVICE']
            hostname=i['HOSTNAME']
            write_result(protocol,service,hostname)
            #print(str(info).split("SERVICE': '")[1].split("',")[0])
        print('protocols and services was checked')
        conn.close()

    except:
        print('Something was wrong...')

_sap_security_abap_protocolisup()