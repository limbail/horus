#!/usr/bin/env python
try:
    import sys, random, os, time, datetime, json
    from datetime import timedelta
    from libs.isbusiness_time import _isbusiness_time as isbt
    import pandas as pd
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


try:
    urls=fd['urls']
except:
    print('Not urls to check, continue...')

# Read config File
with open(horus_root + "horus_files/myconfig.json", "r") as file:
    myconfig = json.load(file)
    
influx_token = myconfig['influx_token']
influx_org = myconfig['influx_org']
influxdb_url = myconfig['influxdb_url']
influx_bucket = myconfig['influx_bucket']

# write to influx
def write_result(rule,value):
    try:
        import influxdb_client
        from influxdb_client import InfluxDBClient, Point, WritePrecision
        from influxdb_client.client.write_api import SYNCHRONOUS
    except ImportError as e:
        print('Module with problems: {0}'.format(e))

    client = influxdb_client.InfluxDBClient(url=influxdb_url, token=influx_token, org=influx_org, bucket_name=influx_bucket, timeout=5, verify_ssl=False)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # alerts
    point = (
    Point("security")
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
    .tag("hardening","hardening")
    .tag("abap_parameters","abap_parameters")
    .field(rule, value)
    )

    write_api.write(bucket=influx_bucket, org=influx_org, record=point)


def checkrules(param,value):
    PVALUE = 'ERROR'

    if type(value) == int or type(value) == float or value.isdigit():
        PVALUE = int(value)
    else:
        PVALUE = str(value)

    # rsau/enable	PVALUE == 1
    if param == 'rsau/enable':
        if PVALUE == 1: return True

    # login/password_downwards_compatibility	PVALUE == 0
    if param == 'login/password_downwards_compatibility':
        if PVALUE == 0: return True

    # rsau/integrity	PVALUE == 1
    if param == 'rsau/integrity':
        if PVALUE == 1: return True

    # rsau/log_peer_address	PVALUE == 1
    if param == 'rsau/log_peer_address':
        if PVALUE == 1: return True

    # rsau/selection_slots	PVALUE >= 10
    if param == 'rsau/selection_slots':
        if PVALUE >= 10: return True

    # rsau/user_selection	PVALUE == 1
    if param == 'rsau/user_selection':
        if PVALUE == 1: return True

    # login/min_password_lng	PVALUE >= 8
    if param == 'login/min_password_lng':
        if PVALUE >= 8: return True

    # login/password_max_idle_initial	PVALUE in range(1, 14)
    if param == 'login/password_max_idle_initial':
        if PVALUE in range(1, 14): return True

    # login/password_expiration_time	PVALUE in range(1, 183)
    if param == 'login/password_expiration_time':
        if PVALUE in range(1, 183): return True

    # login/password_downwards_compatibility	PVALUE == 0
    if param == 'login/password_downwards_compatibility':
        if PVALUE == 0: return True

    # login/password_compliance_to_current_policy	PVALUE == 1
    if param == 'login/password_compliance_to_current_policy':
        if PVALUE == 1: return True

    # icf/reject_expired_passwd	PVALUE == 1
    if param == 'icf/reject_expired_passwd':
        if PVALUE == 1: return True

    # rfc/reject_expired_passwd	PVALUE == 1
    if param == 'rfc/reject_expired_passwd':
        if PVALUE == 1: return True

    # login/min_password_digits	PVALUE >= 1
    if param == 'login/min_password_digits':
        if PVALUE >= 1: return True

    # login/min_password_letters	PVALUE >= 1
    if param == 'login/min_password_letters':
        if PVALUE >= 1: return True

    # login/min_password_lowercase	PVALUE >= 1
    if param == 'login/min_password_lowercase':
        if PVALUE >= 1: return True

    # login/min_password_uppercase	PVALUE >= 1
    if param == 'login/min_password_uppercase':
        if PVALUE >= 1: return True

    # login/min_password_specials	PVALUE >= 1
    if param == 'login/min_password_specials':
        if PVALUE >= 1: return True

    # login/min_password_diff	PVALUE >= 3
    if param == 'login/min_password_diff':
        if PVALUE >= 3: return True

    # login/disable_password_logon	PVALUE >= 1
    if param == 'login/disable_password_logon':
        if PVALUE >= 1: return True

    # login/fails_to_user_lock	PVALUE in range(1, 5)
    if param == 'login/fails_to_user_lock':
        if PVALUE in range(1, 5): return True

    # login/failed_user_auto_unlock	PVALUE == 0
    if param == 'login/failed_user_auto_unlock':
        if PVALUE == 0: return True

    # login/password_max_idle_productive	PVALUE in range(1, 180)
    if param == 'login/password_max_idle_productive':
        if PVALUE in range(1, 180): return True

    # login/password_change_for_SSO	PVALUE == 1
    if param == 'login/password_change_for_SSO':
        if PVALUE == 1: return True

    # login/password_history_size	PVALUE >= 5
    if param == 'login/password_history_size':
        if PVALUE >= 5: return True

    # password_change_waittime	PVALUE >= 5
    if param == 'password_change_waittime':
        if PVALUE >= 5: return True

    # login/ticket_only_by_https	PVALUE == 1
    if param == 'login/ticket_only_by_https':
        if PVALUE == 1: return True

    # login/ticket_only_to_host	PVALUE == 1
    if param == 'login/ticket_only_to_host':
        if PVALUE == 1: return True

    # icf/set_HTTPonly_flag_on_cookies	PVALUE != 1 or PVALUE != 3
    if param == 'icf/set_HTTPonly_flag_on_cookies':
        if PVALUE != 1 or PVALUE != 3: return True

    # rec/client	PVALUE != 'OFF'
    if param == 'rec/client':
        if str(PVALUE) != 'OFF': return True

    # sapgui/nwbc_scripting	PVALUE == 'FALSE'
    if param == 'sapgui/nwbc_scripting':
        if str(PVALUE) != 'OFF': return True

    # sapgui/user_scripting	PVALUE == 'FALSE'
    if param == 'sapgui/user_scripting':
        if str(PVALUE) == 'FALSE': return True

    # sapgui/user_scripting_disable_recording	PVALUE == 'TRUE'
    if param == 'sapgui/user_scripting_disable_recording':
        if str(PVALUE) == 'TRUE': return True

    # sapgui/user_scripting_force_notification	PVALUE == 'TRUE'
    if param == 'sapgui/user_scripting_force_notification':
        if str(PVALUE) == 'TRUE': return True

    # sapgui/user_scripting_per_user	PVALUE == 'TRUE'
    if param == 'sapgui/user_scripting_per_user':
        if str(PVALUE) == 'TRUE': return True

    # sapgui/user_scripting_set_readonly	PVALUE == 'TRUE'
    if param == 'sapgui/user_scripting_set_readonly':
        if str(PVALUE) == 'TRUE': return True

    # snc/enable	PVALUE == 1
    if param == 'snc/enable':
        if PVALUE == 1: return True

    # snc/data_protection/min	PVALUE == 3
    if param == 'snc/data_protection/min':
        if PVALUE == 3: return True

    # snc/data_protection/max	PVALUE == 3
    if param == 'snc/data_protection/max':
        if PVALUE == 3: return True

    # snc/data_protection/use	PVALUE == 3 or PVALUE == 9
    if param == 'snc/data_protection/use':
        if PVALUE == 3 or PVALUE == 9: return True

    # snc/accept_insecure_gui	PVALUE == 0 or PVALUE == 'U'
    if param == 'snc/accept_insecure_gui':
        if PVALUE == 0 or str(PVALUE) == 'U': return True

    # snc/accept_insecure_rfc	PVALUE == 0 or PVALUE == 'U'
    if param == 'snc/accept_insecure_rfc':
        if PVALUE == 0 or str(PVALUE) == 'U': return True

    # snc/accept_insecure_r3int_rfc	PVALUE == 0 or PVALUE == 1
    if param == 'snc/accept_insecure_r3int_rfc':
        if PVALUE == 0 or PVALUE == 1: return True

    # snc/only_encrypted_gui	PVALUE == 1
    if param == 'snc/only_encrypted_gui':
        if PVALUE == 1: return True

    # snc/only_encrypted_rfc	PVALUE == 1
    if param == 'snc/only_encrypted_rfc':
        if PVALUE == 1: return True

    # snc/log_unencrypted_rfc	PVALUE == 2
    if param == 'snc/log_unencrypted_rfc':
        if PVALUE == 2: return True

    # system/secure_communication	PVALUE == 'ON'
    if param == 'system/secure_communication':
        if str(PVALUE) == 'ON': return True

    # gw/acl_mode	PVALUE == 1
    if param == 'gw/acl_mode':
        if PVALUE == 1: return True

    # gw/monitor	PVALUE == 1
    if param == 'gw/monitor':
        if PVALUE == 1: return True

    # gw/sim_mode	PVALUE == 0
    if param == 'gw/sim_mode':
        if PVALUE == 0: return True

    # gw/rem_start	PVALUE == 'DISABLED' or PVALUE == 'SSH_SHELL'
    if param == 'gw/rem_start':
        if str(PVALUE) == 'DISABLED' or str(PVALUE) == 'SSH_SHELL': return True

    # dynp/checkskip1screen	PVALUE == 'ALL'
    if param == 'dynp/checkskip1screen':
        if str(PVALUE) == 'ALL': return True

    # dynp/confirmskip1screen	PVALUE == 'ALL'
    if param == 'dynp/confirmskip1screen':
        if str(PVALUE) == 'ALL': return True

    # auth/check/calltransaction	PVALUE == 2 or PVALUE == 3
    if param == 'dynp/confirmskip1screen':
        if PVALUE == 2 or PVALUE == 3: return True

    # auth/no_check_in_some_cases	PVALUE == 'Y'
    if param == 'auth/no_check_in_some_cases':
        if str(PVALUE) == 'Y': return True

    # auth/object_disabling_active	PVALUE == 'N'
    if param == 'auth/object_disabling_active':
        if str(PVALUE) == 'N': return True

    # rdisp/vbdelete	PVALUE == 0
    if param == 'rdisp/vbdelete':
        if PVALUE == 0: return True

    # rdisp/msserv_internal	PVALUE > 0
    if param == 'rdisp/msserv_internal':
        if PVALUE > 0: return True

    # ms/monitor	PVALUE == 0
    if param == 'ms/monitor':
        if PVALUE == 0: return True

    # ms/admin_port	PVALUE <= 0
    if param == 'ms/admin_port':
        if PVALUE <= 0: return True

    # auth/rfc_authority_check	PVALUE == 1 or PVALUE == 6 or PVALUE == 9
    if param == 'auth/rfc_authority_check':
        if PVALUE == 1 or PVALUE == 6 or PVALUE == 9: return True

    # rfc/callback_security_method	PVALUE == 3
    if param == 'rfc/callback_security_method':
        if PVALUE == 3: return True

    # rfc/selftrust	PVALUE == 0
    if param == 'rfc/selftrust':
        if PVALUE == 0: return True

    # ixml/dtd_restriction	PVALUE == 'expansion' or PVALUE == 'prohibited'
    if param == 'ixml/dtd_restriction':
        if str(PVALUE) == str('expansion') or str(PVALUE) == str('prohibited'): return True

    # login/disable_cpic	PVALUE == 1
    if param == 'login/disable_cpic':
        if PVALUE == 1: return True

    # wdisp/add_xforwardedfor_header	PVALUE == 1 or PVALUE == 'true' or PVALUE == 'TRUE'
    if param == 'wdisp/add_xforwardedfor_header':
        if PVALUE == 1 or str(PVALUE) == 'true' or str(PVALUE) == 'TRUE': return True


def _sap_security_abap_hardening():
    conn_params = {
        'ashost' : fqdn,
        'sysnr' : sap_sysn,
        'client' : sap_client,
        'user' : _get_credentials(instance_id,'ABAP')['username'],
        'passwd' : _get_credentials(instance_id,'ABAP')['password'],
    }

    try:        
        conn = Connection(**conn_params)
        QUERY_TABLE = 'TPFET'
        Fields = ['PFNAME', 'VERSNR', 'PARNAME', 'PSTATE', 'PVALUE' ]
        FIELDS = [{'FIELDNAME':x} for x in Fields]
        data = conn.call("RFC_READ_TABLE", DELIMITER='|', FIELDS=FIELDS, QUERY_TABLE=QUERY_TABLE)
        data = data['DATA']
        df1 = pd.DataFrame(data, columns = ['WA'])
        df1 = df1['WA'].str.split('|', expand=True)
        df1 = df1.rename({0:'PFNAME', 1:'VERSNR', 2:'PARNAME', 3:'PSTATE', 4:'PVALUE'}, axis='columns')
        df1 = df1.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df1 = df1.astype({"VERSNR": int})
        df1 = df1.groupby('PARNAME', group_keys=False).apply(lambda x: x.loc[x.VERSNR.idxmax()])
        #print(df1.loc[df1['PARNAME'] == 'abap/shared_objects_size_MB'])
        #print(df1)

        df2 = pd.read_excel('../horus_files/hardening_parameters.xlsx', index_col=None)
        df2 = df2.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df2 = df2[df2['type_rule'].str.contains('parameter', na=False)]
        df2 = df2[df2['sap_product_type'].str.contains('abap', na=False)]
        df2 = df2[df2.compliant_rule != 'nonimplemented']
        #print(df2)

        for k,v in df2.iterrows():
            sap_product_type = 'abap'
            type_rule = v['type_rule']
            description = v['description']
            snotes = v['snotes']
            rule = v['rule']
            compliant_rule = v['compliant_rule']
            status = 'nonimplemented'
            if v['rule'] in df1.loc[df1['PARNAME'] == v['rule']]['PARNAME']:
                insap_param = df1.loc[df1['PARNAME'] == v['rule']]['PARNAME'][0]
                insap_value = df1.loc[df1['PARNAME'] == v['rule']]['PVALUE'][0]
                rulecheck = checkrules(insap_param, insap_value)
                # compliance:
                # 1 = OK
                # 0 = NO
                # 2 = parameter not found in system, this need more checks... (pending)

                if rulecheck == True:
                    write_result(rule,0)
                else:
                    write_result(rule,1)
            else:
                write_result(rule,2)

        conn.close()

    except:
        print('Something was wrong...')


def execution():
    _sap_security_abap_hardening()

if __name__ == '__main__':
    timeout=2
    p = multiprocessing.Process(target=execution)
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("Timeout raise!: {}".format(timeout))
        p.terminate()
        p.join()
