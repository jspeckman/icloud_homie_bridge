# icloud_homie_bridge
Bridge between iCloud device status and Homie 3 MQTT convention

I wrote this primarily to get battery and location updates from my iphone for use with openHAB, after running into too many issues with the icloud plugin.

This program will log into the specified iCloud account and get battery and location updates for a given device.
That info will then be sent to an mqtt broker using the Homie 3 convention.

Required python modules:
  pyicloud
  homie-python (The homie-3.0.0 branch of https://github.com/bodiroga/homie-python.git)
  
TODO:
  Currently only one iCloud device per account is supported
  
How to run:
  Copy icloud_homie_bridge.py to /usr/local/bin
  Create a config.yaml file following the example file and put it in /etc/icloud
  Copy icloud-homie-bridge.service to /usr/lib/systemd/system/
  Run systemctl daemon-reload
  Run systemctl enable icloud-homie-bridge.service
  Run systemctl start icloud-homie-bridge.service
  
