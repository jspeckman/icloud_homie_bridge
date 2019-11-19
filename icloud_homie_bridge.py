#!/usr/bin/python3

import yaml
import time
from pyicloud import PyiCloudService
from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.property.property_string import Property_String
from homie.node.property.property_integer import Property_Integer
from homie.node.property.property_float import Property_Float
from homie.node.property.property_switch import Property_Switch

server_config = {}
mqtt_config = {}
node_config = {}

def get_config():
  try:
    with open('/etc/icloud/config.yaml') as f:
      # use safe_load instead load
      configMap = yaml.safe_load(f)
  except FileNotFoundError:
    with open('config.yaml') as f:
      configMap = yaml.safe_load(f)

  for person in configMap.items():
    if str(person[0]) != 'mqtt' and str(person[0]) != 'update':
      node_config[person[0]] = {}
      data = person[1]
      for key, value in data.items():
        node_config[person[0]][key] = value
      node_config[person[0]]['cachedLocation'] = True
      node_config[person[0]]['enableLocation'] = True
    elif str(person[0]) == 'mqtt':
      data = person[1]
      for key, value in data.items():
        mqtt_config[key] = value
    else:
      server_config['update'] = {}
      data = person[1]
      for key,  value in data.items():
        server_config['update'][key] = value

def location_status_handler(node, value):
  node_config[node]['enableLocation'] = value
  node_config[node]['location_status'].value = value
  
def location_cache_handler(node, value):
  node_config[node]['cachedLocation'] = value
  node_config[node]['location_cache'].value = value

def play_sound_handler(node):
  for key, item_value in node_config[node]['api'].devices.items():
    if node_config[node]['device'] in str(item_value):
      node_config[node]['api'].devices.get(key).play_sound()

def send_message_handler(node, value):
  for key, item_value in node_config[node]['api'].devices.items():
    if node_config[node]['device'] in str(item_value):
      node_config[node]['api'].devices.get(key).display_message(subject='Message', message="%s" %(value), sounds=True)
  
def bridge_node_refresh_handler(value):
  server_config['update']['interval'] = value
  bridge_node_refresh.value = value
  
def icloud_login():
  for account in node_config.items():
    node_config[account[0]]['api'] = PyiCloudService(node_config[account[0]]['username'], node_config[account[0]]['password'])

def icloud_get_updates():
  icloud_login()
  for node in node_config.items():
    for key, value in node_config[node[0]]['api'].devices.items():
      if node_config[node[0]]['device'] in str(value):
        status = node_config[node[0]]['api'].devices.get(key).status(['batteryStatus'])
        if str(status['deviceStatus']) != 203:
          node_config[node[0]]['batteryStatus'] = status['batteryStatus']
          if node_config[node[0]]['batteryStatus'] != 'Unknown':
            node_config[node[0]]['batteryLevel'] = float(status['batteryLevel']) * 100
          if node_config[node[0]]['enableLocation'] == "ON":
            if node_config[node[0]]['cachedLocation'] == "OFF":
              location = node_config[node[0]]['api'].devices.get(key).location()
              time.sleep(20)
            location = node_config[node[0]]['api'].devices.get(key).location()
            node_config[node[0]]['longitude'] = location['longitude']
            node_config[node[0]]['latitude'] = location['latitude']
          
        node_config[node[0]]['battery_status'].value = node_config[node[0]]['batteryStatus']
        if node_config[node[0]]['batteryStatus'] != 'Unknown':
          node_config[node[0]]['battery_level'].value = node_config[node[0]]['batteryLevel']
        if node_config[node[0]]['enableLocation'] == "ON":
          node_config[node[0]]['location'].value = "%s, %s" %(node_config[node[0]]['latitude'], node_config[node[0]]['longitude'])
        node_config[node[0]]['location_status'].value = node_config[node[0]]['enableLocation']
        node_config[node[0]]['location_cache'].value = node_config[node[0]]['cachedLocation']

get_config()

iCloud = Device_Base(device_id='icloud-bridge', name='iCloud Homie Bridge', mqtt_settings=mqtt_config)
for node in node_config.items():
  node_config[node[0]]['node'] = Node_Base(iCloud, node[0], node[0].title(), node[0])
  iCloud.add_node(node_config[node[0]]['node'])
  
  node_config[node[0]]['battery_status'] = Property_String(node_config[node[0]]['node'], id="battery-status", name="%s Battery Status" % (node[0].title()), settable=False, value=None)
  node_config[node[0]]['node'].add_property(node_config[node[0]]['battery_status'])
  node_config[node[0]]['battery_level'] = Property_Float(node_config[node[0]]['node'], id="battery-level", name="%s Battery Level" % (node[0].title()), settable=False, value=None)
  node_config[node[0]]['node'].add_property(node_config[node[0]]['battery_level'])
  node_config[node[0]]['location'] = Property_String(node_config[node[0]]['node'], id="location", name="%s Location Coordinates" % (node[0].title()), settable=False, value=None)
  node_config[node[0]]['node'].add_property(node_config[node[0]]['location'])
  node_config[node[0]]['location_status'] = Property_Switch(node_config[node[0]]['node'], id="location-status", name="%s Location Status" % (node[0].title()), value=node_config[node[0]]['enableLocation'], set_value = lambda value: location_status_handler(node[0], value))
  node_config[node[0]]['node'].add_property(node_config[node[0]]['location_status'])
  node_config[node[0]]['location_cache'] = Property_Switch(node_config[node[0]]['node'], id="location-cache", name="%s Location Cache" % (node[0].title()), value=node_config[node[0]]['cachedLocation'], set_value = lambda value: location_cache_handler(node[0], value))
  node_config[node[0]]['node'].add_property(node_config[node[0]]['location_cache'])
  node_config[node[0]]['play_sound'] = Property_Switch(node_config[node[0]]['node'], id="play-sound", name="%s Play Sound" % (node[0].title()), retained=False, value=False, set_value = lambda value: play_sound_handler(node[0]))
  node_config[node[0]]['node'].add_property(node_config[node[0]]['play_sound'])
  node_config[node[0]]['send_message'] = Property_String(node_config[node[0]]['node'], id="send-message", name="%s Send Message" % (node[0].title()), retained=False, value=None, set_value = lambda value: send_message_handler(node[0], value))
  node_config[node[0]]['node'].add_property(node_config[node[0]]['send_message'])
  
bridge_node = Node_Base(iCloud, "bridge", "Bridge", "bridge")
iCloud.add_node(bridge_node)

bridge_node_refresh = Property_Integer(bridge_node, id="refresh-timer", name="iCloud Refresh Timer", value=server_config['update']['interval'], set_value = lambda value: bridge_node_refresh_handler(value))
bridge_node.add_property(bridge_node_refresh)

iCloud.start()

def main():
  last_report_time = 0
  
  for node in node_config.items():
    node_config[node[0]]['location_status'].value = node_config[node[0]]['enableLocation']
    node_config[node[0]]['location_cache'].value = node_config[node[0]]['cachedLocation']
    
  while True:
    if (time.time() - last_report_time) > (int(server_config['update']['interval']) * 60):
      icloud_get_updates()
      bridge_node_refresh.value = server_config['update']['interval']
      last_report_time = time.time()
    time.sleep(1)
    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Quitting.")
