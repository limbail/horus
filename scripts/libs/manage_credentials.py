#!/usr/bin/env python
import yaml
import json
from pykeepass import PyKeePass
from .horus_utils import horus_root

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
kp = PyKeePass(horus_root + 'horus_files/.horus.kdbx', password='horus_password')

# get group or create
group = kp.find_groups(name='horus', first=True)
if not group:
    group = kp.add_group(kp.root_group, 'horus')

# add instance id's to list
instance_id_list = []
for item in find("host_dict", output_dic):
    item = item['instance_id']
    instance_id_list.append(item)


def _check_credentials(instance_id,usage):
    try:
        if kp.find_entries(title=instance_id + "_" + usage.upper(), first=True):
            print('Credentials was found, continue...')
            return True
        else:
            print('Credentials was not found, stop here!')
            return False
    except:
        print('Credentials was not found, stop here!')
        return False

def _get_credentials(instance_id,usage):
    try:
        d = {}
        entry = kp.find_entries(title="{}".format(instance_id +"_"+ usage), first=True)
        d['username'] = entry.username
        d['password'] = entry.password
        return d
    except:
        print("Failed to return credentials...")
        raise

#print(_get_credentials('NPL_001','ABAP')['username'])