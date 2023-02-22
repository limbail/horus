#!/usr/bin/env python
try:
    import sys, requests, datetime, json
    import keyring
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

try:
    urls=fd['urls']
except:
    print('Not urls to check, continue...')
    quit()

# Read config File
with open("myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']

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
            write_result(3,url) # slow response
        elif r.status_code == 200:
            print("server is ok")
            write_result(1,url) # normal
        else:
            print("server response is different than RC=200")
            write_result(0,url) # all others errors are bad
    except:
        print('Something was wrong...')
        write_result(0,url)

for url in urls:
    _sapsiteisup(url)
