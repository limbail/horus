
token="tJWSEQ3gphRTxma1FNCks1xwN5y6cXMJEgOqrm8L_1uD8IaqGPcOJdsfmzY-b-wdoqsbqJIr_b_4yGiaP5tJ_Q==" # This must be considered secret, save this in keyring :)

import influxdb_client, os, time
import random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

org = "my-org"
url = "http://localhost:8086/"
bucket_name = 'SapMonitoring'
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, bucket_name=bucket_name)


# fuckit:
"""
start = "2000-01-01T00:00:00Z"
stop = "2030-01-01T00:00:00Z"
delete_api = client.delete_api()
delete_api.delete(start, stop, '_measurement="systeminfo"', bucket=bucket_name, org="my-org")
"""

# fuckit hard:
"""
influx delete --bucket SapMonitoring --org my-org --start 2000-01-01T00:00:00Z --stop 2030-01-01T00:00:00Z --token tJWSEQ3gphRTxma1FNCks1xwN5y6cXMJEgOqrm8L_1uD8IaqGPcOJdsfmzY-b-wdoqsbqJIr_b_4yGiaP5tJ_Q==
"""


# write:
bucket="SapMonitoring"
write_api = client.write_api(write_options=SYNCHRONOUS)

# alerts
point = (
Point("alerts")
.tag("fqdn", "192.168.50.179")
.tag("sid", "NPA")
.tag("environment", "dev")
.tag("sysn", "01")
.tag("client", "001")
.field("alert_name", "some name")
.field("alert_importance", 1)
)

write_api.write(bucket=bucket, org="my-org", record=point)


number1 = random.randint(0, 1000)
number2 = random.randint(0, 1000)
number3 = random.randint(0, 1000)
number4 = random.randint(0, 1000)

point = (
Point("monitoring")
.tag("fqdn", "192.168.50.179")
.tag("sid", "NPA")
.tag("environment", "dev")
.tag("sysn", "01")
.tag("client", "001")
.field("dialog_time", number1)
.field("batch_time", number2)
.field("http", number3)
.field("https", number4)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "localhost")
.tag("sid", "NPB")
.tag("environment", "pro")
.tag("sysn", "01")
.tag("client", "001")
.field("dialog_time", number1)
.field("batch_time", number2)
.field("http", number3)
.field("https", number4)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "192.168.50.111")
.tag("sid", "NPC")
.tag("environment", "dev")
.tag("sysn", "01")
.tag("client", "001")
.field("dialog_time", number1)
.field("batch_time", number2)
.field("http", number3)
.field("https", number4)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "192.168.50.222")
.tag("sid", "NPD")
.tag("environment", "dev")
.tag("sysn", "01")
.tag("client", "001")
.field("dialog_time", number1)
.field("batch_time", number2)
.field("http", number3)
.field("https", number4)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "192.168.50.179")
.tag("sid", "NPA")
.tag("environment", "dev")
.tag("sysn", "01")
.tag("client", "001")
.field("isup", 0)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "localhost")
.tag("sid", "NPB")
.tag("environment", "pro")
.tag("sysn", "01")
.tag("client", "001")
.field("isup", 1)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "localhost")
.tag("sid", "NPC")
.tag("environment", "pro")
.tag("sysn", "01")
.tag("client", "001")
.field("isup", 1)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "localhost")
.tag("sid", "NPD")
.tag("environment", "pro")
.tag("sysn", "01")
.tag("client", "001")
.field("isup", 0)
)

write_api.write(bucket=bucket, org="my-org", record=point)

point = (
Point("monitoring")
.tag("fqdn", "localhost")
.tag("sid", "NPD")
.tag("environment", "pro")
.tag("sysn", "01")
.tag("client", "001")
.field("isupdate", 0)
)

write_api.write(bucket=bucket, org="my-org", record=point)

print("finish writing shits")

# System info

point = (
Point("systeminfo")
.tag("fqdn", "localhost")
.tag("sid", "NPD")
.tag("environment", "pro")
.tag("sysn", "01")
.tag("client", "100")
.field("project", "project name")
.field("version", "2.0")
.field("sid", "NPD")
.field("client", "100")
)

write_api.write(bucket=bucket, org="my-org", record=point)

