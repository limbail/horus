#!/usr/bin/env python
from datetime import timedelta, datetime
import urllib.parse
from cryptography import x509
import socket
import ssl
import sys
import json
from libs.isbusiness_time import _isbusiness_time as isbt
from libs.horus_utils import horus_root
from libs.manage_credentials import _check_credentials, _get_credentials
import multiprocessing, time

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

# convert multiple args to lists
urls=urls.split(",")

# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']
influx_timeout = myconfig['influx_timeout']

def now():
    return datetime.utcnow().replace(tzinfo=utc)

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
    Point("alerts")
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
    .field("url_expiration", status)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

def check_url_expiration_logic(host,port):
    try:
        host=host.replace('http://','')
        host=host.replace('https://','')
        host=host.replace('www.','')

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.create_connection((host, port))
        sock.settimeout(2)

        ssock = context.wrap_socket(sock, server_hostname = host)

        data = ssock.getpeercert(True)
        pem_data = ssl.DER_cert_to_PEM_cert(data)
        cert_data = x509.load_pem_x509_certificate(str.encode(pem_data))
        certExpires = datetime.strptime(str(cert_data.not_valid_after), '%Y-%m-%d %H:%M:%S')
        daysToExpiration = (certExpires - datetime.now()).days

        if daysToExpiration <= 30:
            write_result(daysToExpiration,host)

    except TimeoutError:
        return((f'critical: Timeout! in {host}'))
    except:
        return((f'critical: Unexpected Error! in {host}'))

def _check_url_expiration(url):
    fullurl=url
    urlparts=urllib.parse.urlsplit(fullurl)
    scheme=urlparts.scheme
    hostname=urlparts.hostname
    port=urlparts.port

    if scheme == 'http' and not port: port=80
    if scheme == 'https' and not port: port=443
    if scheme != 'http':
        try:
            print('checking: ' + str(scheme) + '://' + str(hostname) + ':' + str(port))
            check_url_expiration_logic(hostname,port).split(':')
        except:
            pass

def execution():
    for url in urls:
        _check_url_expiration(url)

if __name__ == '__main__':
    timeout=10
    p = multiprocessing.Process(target=execution)
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("Timeout raise!: {}".format(timeout))
        p.terminate()
        p.join()
    