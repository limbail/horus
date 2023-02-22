#!/usr/bin/env python
try:
    import sys, random, os, time, json, glob
    import keyring
    from pyrfc import Connection, get_nwrfclib_version
except ImportError as e:
    print('Module with problems: {0}'.format(e))
#print(sys.argv[1:])

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

# Read config File
with open("myconfig.json", "r") as file:
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
    .tag("fqdn", fqdn)
    .tag("sap_sid", sap_sid)
    .tag("sap_client", sap_client)
    .tag("sap_sysn", sap_sysn)
    .tag("product_type", product_type)
    .tag("environment", environment)
    .tag("os_findcore", "os_findcore")
    .field("directory", status)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)
    quit()

# Using regex to find core in directories:
ldir=['/usr/sap/???/D*/work/',
    '/usr/sap/???/J*/work/',
    '/usr/sap/???/W*/work/']

def _os_findcore():
    for d in ldir:
        f=glob.glob(d + '*core*')
        if f:
            print(f)
            write_result(f)
_os_findcore()
