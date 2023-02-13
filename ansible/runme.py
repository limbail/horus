import subprocess
if __name__ == '__main__':
    subprocess.call('cd /home/limbail/Projects/SapTool/ansible', shell=True)
    subprocess.run(['pipenv', 'shell'])
    subprocess.call('cd /home/limbail/Projects/SapTool/ansible', shell=True) 
    subprocess.run(['ansible-playbook', '-i', 'my_inventory.ini', 'playbook.yml'])

#dirty but work:P
# with: pm2 start runme.py --name job_execute_playbook --interpreter python3 --restart-delay 60000