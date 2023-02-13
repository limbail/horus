#!/usr/bin/python
try:
    import sys, random, os, time, json
    import datetime as dt
    from datetime import timedelta
    import keyring
    from pyrfc import Connection, get_nwrfclib_version
except ImportError as e:
    print('Module with problems: {0}'.format(e))

# define some variables
fqdn=sys.argv[1]
sap_sid=sys.argv[2]
sap_client=sys.argv[3]
sap_sysn=sys.argv[4]
product_type=sys.argv[5]
environment=sys.argv[6]
urls=''

# Read config File
with open("myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']

# write to influx
def write_result(stuckjobs):
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
    .tag("sap_abap_jobs", "sap_abap_jobs")
    .field("abap_stuck_jobs", stuckjobs)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

try:
    if keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'):
        print("Autorization was found, continue...")   
    else: quit()
except: 
    print('print("Not autorization was found")')
    quit()

def _sap_abap_jobs():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : 'limbail',
        'passwd' : keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'),
    }

    try:
        sumtotal=0
        conn = Connection(**conn_params)

        sapdate=conn.call("GET_SYSTEM_TIME_REMOTE")
        sapdate=sapdate['K_DATE']

        QUERY_TABLE = 'TBTCO'
        options = [{'TEXT': "SDLSTRTDT = '{}'".format(sapdate)} and {'TEXT': "STATUS = 'R'"}]
        Fields = ['STRTDATE', 'STRTTIME']
        FIELDS = [{'FIELDNAME':x} for x in Fields]
        jobs = conn.call("RFC_READ_TABLE", DELIMITER='|', FIELDS=FIELDS, QUERY_TABLE=QUERY_TABLE, OPTIONS=options )
        
        now = dt.datetime.now()    

        stuckjobs=0
        for item in jobs['DATA']:
            d=item['WA'].split('|')[0]
            t=item['WA'].split('|')[1]
            d1 = dt.datetime.strptime(d, "%Y%m%d")
            mytime = dt.datetime.strptime(t,'%H%M%S').time()
            jobdt = dt.datetime.combine(d1, mytime)

            # get difference
            delta = now - jobdt

            #print (delta)
            sec_diff = delta.total_seconds()
            #print('difference in seconds:', sec_diff)
            min_diff = sec_diff / 60
            #print('difference in minutes:', min_diff)

            #print(item)
            if min_diff > 1440:
                stuckjobs += 1 # remove negative datetime object and compare diff to now, more than...
                write_result(stuckjobs)
            else:
                write_result(0)

        write_result(0)
    except:
        raise


_sap_abap_jobs()