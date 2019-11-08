#!/usr/bin/python3

import yaml
import homie
import time
from pyicloud import PyiCloudService

server_config = {}
homie_config = {}
node_config = {}

def get_config():
  with open('/etc/icloud/config.yaml') as f:
    # use safe_load instead load
    configMap = yaml.safe_load(f)

  for person in configMap.items():
    if str(person[0]) != 'homie' and str(person[0]) != 'update':
      node_config[person[0]] = {}
      data = person[1]
      for key, value in data.items():
        node_config[person[0]][key] = value
      node_config[person[0]]['cachedLocation'] = "ON"
      node_config[person[0]]['enableLocation'] = "ON"
    elif str(person[0]) == 'homie':
      data = person[1]
      for key, value in data.items():
        homie_config[key] = value
    else:
      server_config['update'] = {}
      data = person[1]
      for key,  value in data.items():
        server_config['update'][key] = value

def location_status_handler(property,  value):
  node_config[property.node.nodeId]['enableLocation'] = value
  property.update(value)
  
def location_cache_handler(property,  value):
  node_config[property.node.nodeId]['cachedLocation'] = value
  property.update(value)

def play_sound_handler(property,  value):
  for key, item_value in node_config[property.node.nodeId]['api'].devices.items():
    if node_config[property.node.nodeId]['device'] in str(item_value):
      node_config[property.node.nodeId]['api'].devices.get(key).play_sound()

def send_message_handler(property, value):
  for key, item_value in node_config[property.node.nodeId]['api'].devices.items():
    if node_config[property.node.nodeId]['device'] in str(item_value):
      node_config[property.node.nodeId]['api'].devices.get(key).display_message(subject='Message', message="%s" %(value), sounds=True)
  
def bridge_node_refresh_handler(property,  value):
  server_config['update']['interval'] = value
  property.update(value)
  
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
          
        node_config[node[0]]['battery_status'].update(node_config[node[0]]['batteryStatus'])
        if node_config[node[0]]['batteryStatus'] != 'Unknown':
          node_config[node[0]]['battery_level'].update(node_config[node[0]]['batteryLevel'])
        if node_config[node[0]]['enableLocation'] == "ON":
          node_config[node[0]]['location'].update("%s, %s" %(node_config[node[0]]['latitude'], node_config[node[0]]['longitude']))
        node_config[node[0]]['location_status'].update(node_config[node[0]]['enableLocation'])
        node_config[node[0]]['location_cache'].update(node_config[node[0]]['cachedLocation'])

get_config()

iCloud = homie.Device(homie_config)
for node in node_config.items():
  node_config[node[0]]['node'] = iCloud.addNode(node[0], node[0].title(), node[0])
  node_config[node[0]]['battery_status'] = node_config[node[0]]['node'].addProperty("battery-status", "%s Battery Status" % (node[0].title()), datatype="string")
  node_config[node[0]]['battery_level'] = node_config[node[0]]['node'].addProperty("battery-level", "%s Battery Level" % (node[0].title()), datatype="float")
  node_config[node[0]]['location'] = node_config[node[0]]['node'].addProperty("location", "%s Location Coordinates" % (node[0].title()), datatype="string")
  node_config[node[0]]['location_status'] = node_config[node[0]]['node'].addProperty("location-status", "%s Location Status" % (node[0].title()), datatype="enum", format="ON,OFF")
  node_config[node[0]]['location_cache'] = node_config[node[0]]['node'].addProperty("location-cache", "%s Location Cache" % (node[0].title()), datatype="enum", format="ON,OFF")
  node_config[node[0]]['play_sound'] = node_config[node[0]]['node'].addProperty("play-sound", "%s Play Sound" % (node[0].title()),  datatype="enum", format="ON", retained=False)
  node_config[node[0]]['send_message'] = node_config[node[0]]['node'].addProperty("send-message", "%s Send Message" % (node[0].title()),  datatype="string", retained=False)
  
bridge_node = iCloud.addNode("bridge", "Bridge", "bridge")
bridge_node_refresh = bridge_node.addProperty("refresh-timer", "iCloud Refresh Timer", datatype="integer")

def main():
  last_report_time = 0
  
  iCloud.setFirmware("iCloud Homie Bridge", "0.0.2")
  bridge_node_refresh.settable(bridge_node_refresh_handler)
  for node in node_config.items():
    node_config[node[0]]['location_status'].settable(location_status_handler)
    node_config[node[0]]['location_cache'].settable(location_cache_handler)
    node_config[node[0]]['play_sound'].settable(play_sound_handler)
    node_config[node[0]]['send_message'].settable(send_message_handler)

  iCloud.setup()
  
  bridge_node_refresh.update(server_config['update']['interval'])
  for node in node_config.items():
    node_config[node[0]]['location_status'].update(node_config[node[0]]['enableLocation'])
    node_config[node[0]]['location_cache'].update(node_config[node[0]]['cachedLocation'])
    
  while True:
    if (time.time() - last_report_time) > (int(server_config['update']['interval']) * 60):
      icloud_get_updates()
      bridge_node_refresh.update(server_config['update']['interval'])
      last_report_time = time.time()
    time.sleep(1)
    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Quitting.")
