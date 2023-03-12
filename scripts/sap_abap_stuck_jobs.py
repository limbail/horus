#!/usr/bin/env python
try:
    import sys, random, os, time, json
    import datetime as dt
    from datetime import timedelta
    from libs.isbusiness_time import _isbusiness_time as isbt
    from pyrfc import Connection, get_nwrfclib_version
    from libs.horus_utils import horus_root
    from libs.manage_credentials import _check_credentials, _get_credentials
    import multiprocessing, time

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


# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']
influx_timeout = myconfig['influx_timeout']

# write to influx
def write_result(stuckjobs):
    try:
        import influxdb_client
        from influxdb_client import InfluxDBClient, Point, WritePrecision
        from influxdb_client.client.write_api import SYNCHRONOUS
    except ImportError as e:
        print('Module with problems: {0}'.format(e))

    client = influxdb_client.InfluxDBClient(url=influxdb_url, token=influx_token, org=influx_org, bucket_name=influx_bucket, timeout=influx_timeout, verify_ssl=False)
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
    .tag("sap_abap_jobs", "sap_abap_jobs")
    .field("abap_stuck_jobs", stuckjobs)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)


def _sap_abap_jobs():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : _get_credentials(instance_id,'ABAP')['username'],
        'passwd' : _get_credentials(instance_id,'ABAP')['password'],
    }

    try:
        sumtotal=0
        conn = Connection(**conn_params)

        sapdate=conn.call("GET_SYSTEM_TIME_REMOTE")
        startdt = dt.datetime.strptime(str(sapdate['K_DATE']), '%Y%m%d') - timedelta(days=30)
        startdt = startdt.strftime('%Y%m%d')
        
        QUERY_TABLE = 'TBTCO'
        options = [
        {'TEXT': "SDLSTRTDT >= '{}'".format(startdt)},
        {'TEXT': "AND STATUS = 'R'"}]
        
        Fields = ['STRTDATE', 'STRTTIME']
        FIELDS = [{'FIELDNAME':x} for x in Fields]
        jobs = conn.call("RFC_READ_TABLE", DELIMITER='|', FIELDS=FIELDS, QUERY_TABLE=QUERY_TABLE, OPTIONS=options)
              
        now = dt.datetime.now()
        stuckjobs=0
        for item in jobs['DATA']:
            d=item['WA'].split('|')[0]
            t=item['WA'].split('|')[1]
            d1 = dt.datetime.strptime(d, "%Y%m%d")
            mytime = dt.datetime.strptime(t,'%H%M%S').time()
            jobdt = dt.datetime.combine(d1, mytime)

            delta = now - jobdt
            sec_diff = delta.total_seconds()
            min_diff = sec_diff / 60

            if min_diff > 1440:
                stuckjobs += 1

        write_result(stuckjobs)
        conn.close()            
        
    except:
        raise


def execution():
    _sap_abap_jobs()
    
if __name__ == '__main__':
    timeout=10
    p = multiprocessing.Process(target=execution)
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("Timeout raise!: {}".format(timeout))
        p.terminate()
        p.join()
