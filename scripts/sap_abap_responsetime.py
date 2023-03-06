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
action=fd['action']


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
def write_result(dialog,background,rfc,http,https):
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
    .tag("sap_responsetime","sap_responsetime")
    .field("rtime_dialog", dialog)
    .field("rtime_background", background)
    .field("rtime_rfc", rfc)
    .field("rtime_http", http)
    .field("rtime_https", https)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)


def _getsaprtimes():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : _get_credentials(instance_id,'ABAP')['username'],
        'passwd' : _get_credentials(instance_id,'ABAP')['password'],
    }

    try:
        conn = Connection(**conn_params)
        actualserver=conn.call("GENERAL_GET_APP_SERVER_NAME")['SERVER_NAME'] # we will get the data from system we are logged
        sapdate=conn.call("GET_SYSTEM_TIME_REMOTE")

        # dont get more than 5 min in the past!, we want fast requests :)
        startdt = datetime.datetime.strptime(str(sapdate['K_DATE']) +' '+ str(sapdate['K_TIME']), '%Y%m%d %H%M%S') - timedelta(hours=0, minutes=5) # start date is system datetime sub 5 min.
        enddt = datetime.datetime.strptime(str(sapdate['K_DATE']) +' '+ str(sapdate['K_TIME']), '%Y%m%d %H%M%S')# - timedelta(hours=0, minutes=10) # end date is system actual datetime.
        
        sd=conn.call("SAPWL_SNAPSHOT_FROM_REMOTE_SYS", SELECT_SERVER=actualserver, READ_START_DATE=startdt.date(),READ_START_TIME=startdt.time(),READ_END_DATE=enddt.date(),READ_END_TIME=enddt.time() )
        summary=sd['SUMMARY']
        for entry in summary:
            print(entry['TASKTYPE'])
            if entry['TASKTYPE'] == 'DIALOG':
                dialog=round(entry['RESPTI'] / entry['COUNT'])
            else: dialog=0
            if entry['TASKTYPE'] == 'BCKGRD':
                background=round(entry['RESPTI'] / entry['COUNT'])
            else: background=0
            if entry['TASKTYPE'] == 'RFC':
                rfc=round(entry['RESPTI'] / entry['COUNT'])
            else: rfc=0
            if entry['TASKTYPE'] == 'HTTP':
                http=round(entry['RESPTI'] / entry['COUNT'])
            else: http=0
            if entry['TASKTYPE'] == 'HTTPS':
                https=round(entry['RESPTI'] / entry['COUNT'])
            else: https=0

        write_result(dialog,background,rfc,http,https)

        conn.close()
    except:
        print('Something was wrong...')

_getsaprtimes()