#!/usr/bin/env python
try:
    import sys, random, os, time, json
    import keyring
    from pyrfc import Connection, get_nwrfclib_version
except ImportError as e:
    print('Module with problems: {0}'.format(e))

"""
# define some variables
fqdn="192.168.50.179"
sap_sid="NPL"
sap_client="001"
sap_sysn="00"
product_type="abap"
environment="dev"
urls=''
"""

# raw argv
raw_argv = sys.argv[1]
print(raw_argv)
# convert raw argv to dict object
fd = eval(raw_argv)
print(type(fd))

# define variables
fqdn=fd['fqdn']
sap_sid=fd['sap_sid']
sap_client=fd['sap_client']
sap_sysn=fd['sap_sysn']
product_type=fd['product_type']
environment=fd['environment']

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
def write_result(sap_memory_total,sap_memory_used):
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
    .tag("fqdn", fqdn)
    .tag("sap_sid", sap_sid)
    .tag("sap_client", sap_client)
    .tag("sap_sysn", sap_sysn)
    .tag("product_type", product_type)
    .tag("environment", environment)
    .tag("sap_memory","sap_memory")
    .field("sap_memory_total", sap_memory_total)
    .field("sap_memory_used", sap_memory_used)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

try:
    if keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'):
        print("Autorization was found, continue...")   
    else: quit()
except: 
    print('print("Not autorization was found")')
    quit()

def _sap_abap_memory():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : 'limbail',
        'passwd' : keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'),
    }

    try:
        conn = Connection(**conn_params)
        manydata=conn.call("SAPTUNE_GET_SUMMARY_STATISTIC")
        currentused=conn.call("/SDF/MON_USER_MEMORY")

        for k,v in manydata["EXTENDED_MEMORY_USAGE"].items():
            if 'TOTAL' in k: 
                sap_memory_total = v
                #print(sap_memory_total)

        sumtotal=0
        for k,v in currentused.items():
            for item in v:
                sumtotal += item['MEMSUMKB'] / 1000
        sap_memory_used=round(sumtotal)

        write_result(sap_memory_total,sap_memory_used)

    except:
        print('Something was wrong...')

_sap_abap_memory()