import sys
import yaml
from pyicloud import PyiCloudService

statusMap = {}

with open('config.yaml') as f:
  # use safe_load instead load
  configMap = yaml.safe_load(f)
  
for person in configMap.items():
  if person[0] != 'homie' and person[0] != 'update':
    statusMap[person[0]] = {}
    data = person[1]
    for key, value in data.items():
      statusMap[person[0]][key] = value

for person in statusMap.items():
  statusMap[person[0]]['api'] = PyiCloudService(statusMap[person[0]]['username'], statusMap[person[0]]['password'])
  
  if statusMap[person[0]]['api'].requires_2fa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = statusMap[person[0]]['api'].trusted_devices
    for i, device in enumerate(devices):
        print("  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber'))))

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not statusMap[person[0]]['api'].send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not statusMap[person[0]]['api'].validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

for person in statusMap.items():
  print("Devices registered to ", person[0])
  for key, value in statusMap[person[0]]['api'].devices.items():
    print(key,  value)
