#!/usr/bin/env python
import getpass
import argparse
import json
import keyring

# Parse Arguments
parser = argparse.ArgumentParser(description="Create some secrets",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-F", "--first configuration", action="store_true", help="Configure connection to Horus")
args = parser.parse_args()
config = vars(args)

# Add secret
if config['first configuration'] == True:
    print('Enter credentials that will be used:')
    sid = input('sid: ')
    product_type = input('abap,java,opentext,contentserver,hana,site: ')
    fqdn = input('hostname: ')
    username = input('Username: ')
    password = getpass.getpass('Password: ')

    try:
        if username and password:
            keyring.set_password(sid+'_'+product_type+'_'+fqdn,username,password)
            print('Token saved in Keyring')
        else:
            print('Configuration fail')
    except:
        raise
    quit()