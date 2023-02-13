#!/usr/bin/python
try:
    import sys, random, os, time, json
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
def write_result(buffer_name,buffer_avail_size,buffer_used_space,buffer_swap,buffer_hitratio):
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
    .tag("buffer_name",buffer_name)
    .field("buffer_avail_size", buffer_avail_size,)
    .field("buffer_used_space", buffer_used_space)
    .field("buffer_swap", buffer_swap)
    .field("buffer_hitratio", buffer_hitratio)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

try:
    if keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'):
        print("Autorization was found, continue...")   
    else: quit()
except: 
    print('print("Not autorization was found")')
    quit()

def _sapabapbuffer():
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

        for data in manydata["BUFFER_STATISTIC_64"]:
            buffer_name = data["NAME"]
            buffer_avail_size = data["AVAIL_SIZE"]
            buffer_used_space = data["USED_SPACE"]
            buffer_swap = data["SWAP"]
            buffer_hitratio = data["HITRATIO"]
            write_result(buffer_name,buffer_avail_size,buffer_used_space,buffer_swap,buffer_hitratio)
    except:
        print("Connection to SAP fail.")

_sapabapbuffer()