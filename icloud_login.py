import sys
import yaml
from pyicloud import PyiCloudService

node_config = {}

try:
  with open('/etc/icloud/config.yaml') as f:
    # use safe_load instead load
    configMap = yaml.safe_load(f)
except FileNotFoundError:
  with open('config.yaml') as f:
    configMap = yaml.safe_load(f)
  
for account in configMap.items():
  if 'account' in account[0]:
    for device in account[1].items():
      if 'device' in device[0]:
        node_config[device[1]['device_name']] = {}
        node_config[device[1]['device_name']]['icloud_device_id'] = device[1]['device_id']
        node_config[device[1]['device_name']]['icloud_username'] = account[1]['username']
        node_config[device[1]['device_name']]['icloud_password'] = account[1]['password']

for account in node_config.items():
  node_config[account[0]]['api'] = PyiCloudService(node_config[account[0]]['icloud_username'], node_config[account[0]]['icloud_password'])
  
  if node_config[account[0]]['api'].requires_2fa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = node_config[account[0]]['api'].trusted_devices
    for i, device in enumerate(devices):
        print("  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber'))))

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not node_config[account[0]]['api'].send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not node_config[account[0]]['api'].validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

for account in node_config.items():
  print("Devices registered to", account[0])
  for key, value in node_config[account[0]]['api'].devices.items():
    print('Device ID: ', key)
    print('Description: ', value)
