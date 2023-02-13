#!/usr/bin/python
try:
    import sys, random, os, time, json
    import keyring
    from pyrfc import Connection, get_nwrfclib_version
except ImportError as e:
    print('Module with problems: {0}'.format(e))
#print(sys.argv[1:])


# define some variables
fqdn=sys.argv[1]
sap_sid=sys.argv[2]
sap_client=sys.argv[3]
sap_sysn=sys.argv[4]
product_type=sys.argv[5]
environment=sys.argv[6]

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

    token="tJWSEQ3gphRTxma1FNCks1xwN5y6cXMJEgOqrm8L_1uD8IaqGPcOJdsfmzY-b-wdoqsbqJIr_b_4yGiaP5tJ_Q=="
    org = "my-org"
    url = "http://localhost:8086/"
    bucket_name = "SapMonitoring"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, bucket_name=bucket_name)
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
    .field("abap_isup", status)
    )

    write_api.write(bucket=bucket_name, org="my-org", record=point)
    quit()

try:
    if keyring.get_password(sap_sid +'_'+ product_type +'_'+ fqdn,'limbail'):
        print("Autorization was found, continue...")   
    else: quit()
except: 
    print('print("Not autorization was found")')
    write_result(0) # write error if can't connect to SAP
    quit()

def _sapabapisup():
    # pyrfc connection params
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : 'limbail',
        'passwd' : keyring.get_password(sys.argv[2] +'_'+ sys.argv[5] +'_'+ sys.argv[1],'limbail'),
    }

    try:
        conn = Connection(**conn_params)
        if conn.alive == True:
            alive=True
            conn.close()
            print("server is up")
            write_result(1)
        else: 
            print("server is down!")
            write_result(0)
    except:
        print("server is down!")
        write_result(0)

_sapabapisup()
