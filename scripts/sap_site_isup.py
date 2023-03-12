#!/usr/bin/env python
try:
    import sys, requests, datetime, json
    from libs.isbusiness_time import _isbusiness_time as isbt
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
#if _check_credentials(instance_id,'abap') != True: quit()


try:
    urls=fd['urls']
except:
    print('Not urls to check, continue...')
    quit()

# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']
influx_timeout = myconfig['influx_timeout']

# convert multiple args to lists
urls=urls.split(",")

# write to influx
def write_result(status,url):
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
    .tag("url", url)
    .field("site_isup", status)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

def _sapsiteisup(url):
    try:
        r = requests.head(url)
        elapsed = r.elapsed
        
        if elapsed > datetime.timedelta(seconds=2):
            print("server is slow!")
            write_result(3,url)
        elif r.status_code == 200:
            print("server is ok")
            write_result(1,url)
        else:
            print("server response is different than RC=200")
            write_result(0,url)
    except Exception:
        write_result(0,url)
        pass

def execution():
    for url in urls:
        _sapsiteisup(url)

if __name__ == '__main__':
    timeout=10
    p = multiprocessing.Process(target=execution)
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("Timeout raise!: {}".format(timeout))
        p.terminate()
        p.join()
