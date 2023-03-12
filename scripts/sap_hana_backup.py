#!/usr/bin/env python
try:
    import sys, random, os, time, json
    from libs.isbusiness_time import _isbusiness_time as isbt
    from libs.horus_utils import horus_root
    from libs.manage_credentials import _check_credentials, _get_credentials
    import multiprocessing, time
    from hdbcli import dbapi

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
db_type=fd['db_type']


# Checks before execution
if isbt(isbt_start,isbt_end) != True: quit()
if product_type != 'database' or db_type != 'hana': quit()
if _check_credentials(instance_id,'BBDD') != True: quit()


# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)

influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']
influx_timeout = myconfig['influx_timeout']


# write to influx
def write_result(backup_id,backup_status,backup_date):
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
    .tag("backup", "backup")
    .tag("backup_id", backup_id)
    .tag("backup_date", backup_date)
    .field("backup_status", backup_status)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)
    quit()

#Backup
#"SELECT top 1 sys_start_time FROM SYS.M_BACKUP_CATALOG where entry_type_name = 'complete data backup' and state_name='successful'order by entry_id asc;"
#Logs
#"SELECT top 1 sys_start_time FROM SYS.M_BACKUP_CATALOG where entry_type_name = 'log backup' and state_name='successful' order by entry_id asc;"

address = fqdn,
port = "39{}7".format(sap_sysn),
user = _get_credentials(instance_id,'BBDD')['username'],
password = _get_credentials(instance_id,'BBDD')['password'],


# hana: successful, failed, running, cancel pending or canceled - horus: 'null'
def _check_hana_backup():
    conn = dbapi.connect(
        address = fqdn,
        port = "39{}7".format(sap_sysn),
        user = _get_credentials(instance_id,'BBDD')['username'],
        password = _get_credentials(instance_id,'BBDD')['password'],
    )

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT top 1 BACKUP_ID, STATE_NAME, UTC_START_TIME FROM SYS.M_BACKUP_CATALOG where entry_type_name = 'complete data backup' order by entry_id asc;")
        result = cursor.fetchone()
        l_backup=list(result)
        if len(l_backup) > 1:
            backup_id=str(l_backup[0])
            backup_status=str(l_backup[1])
            backup_date=str(l_backup[2])
            print (backup_id,backup_status,backup_date)
            write_result(backup_id,backup_status,backup_date)
        else:
            write_result('NaN','NaN','NaN')
    except:
        raise


def execution():
    if product_type == 'hana':
        _check_hana_backup()
    if product_type == 'sybase':
        print('sybase')
    if product_type == 'db2':
        print('db2')
    if product_type == 'oracle':
        print('oracle')
    if product_type == 'mysql':
        print('mysql')


if __name__ == '__main__':
    timeout=10
    p = multiprocessing.Process(target=execution)
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("Timeout raise!: {}".format(timeout))
        write_result('NaN','NaN','NaN')        
        p.terminate()
        p.join()
