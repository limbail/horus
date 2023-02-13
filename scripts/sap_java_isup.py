#!/usr/bin/python
try:
    import sys, requests, datetime, json
    import keyring
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
try:
    urls=sys.argv[7]
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
    .field("java_isup", status)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

def _sapjavaisup(url):
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
        print("server is unknown state!")
        write_result(0,url)

for url in urls:
    _sapjavaisup(url)
