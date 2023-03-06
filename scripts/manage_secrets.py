#!/usr/bin/env python
import yaml
import json
from pykeepass import PyKeePass
from libs.horus_utils import horus_root
import getpass
import argparse

horus_root = horus_root()

# to find inner value in yaml
def find(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result

with open(horus_root + 'ansible/my_inventory.yaml', 'r') as file:
    yaml_file = yaml.safe_load(file)

with open(horus_root + 'horus_files/tmp/my_inventory.json', 'w') as json_file:
    json.dump(yaml_file, json_file)

output_str = json.dumps(json.load(open(horus_root + 'horus_files/tmp/my_inventory.json')), indent=2)
output_dic = json.loads(output_str)

# load database
kp = PyKeePass(horus_root + 'horus_files/.horus.kdbx', password='horus_password') # need .env this

# get group or create
group = kp.find_groups(name='horus', first=True)
if not group:
    group = kp.add_group(kp.root_group, 'horus')

# add instance id's to list
instance_id_list = []
for item in find("host_dict", output_dic):
    item = item['instance_id']
    instance_id_list.append(item)

# Parse Arguments
parser = argparse.ArgumentParser(description="Store secrets to be used in horus connections",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-S", "--store secret", action="store_true", help="store secrets into horus .kdbx")
args = parser.parse_args()
config = vars(args)

#entry = kp.find_entries(title='facebook', first=True)

# Add secret
if config['store secret'] == True:
    print('Enter instance id you want to add:')
    entry_instance_id = input('instance_id: ').upper()

    if entry_instance_id not in instance_id_list:
        print('Error: instance_id must be exist in horus inventory before create a credential.')
        quit()

    accepted_usages = ['ABAP', 'BBDD']
    entry_usage = input('{}'.format(accepted_usages) + ": ").upper()

    if entry_usage not in accepted_usages:
        print('Error: entry_usage must be one of {}.'.format(accepted_usages))
        quit()

    username = input('username: ')
    password = getpass.getpass(prompt='Password: ', stream=None)
    password_again = getpass.getpass(prompt='Password again: ', stream=None)
        
    try:
        if entry_instance_id and entry_usage and password:
            if password == password_again:
                print('Secret saved!')
                kp.add_entry(group, entry_instance_id + "_" + entry_usage, username, password)
                kp.save()
            else:
                print('Password not match!, try again.')
        else:
            print('Configuration fail!')
    except:
        raise

