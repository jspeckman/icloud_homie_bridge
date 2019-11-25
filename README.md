# icloud_homie_bridge
Bridge between iCloud device status and Homie 3 MQTT convention

I wrote this primarily to get battery and location updates from my iphone for use with openHAB, after running into too many issues with the icloud plugin.

This program will log into the specified iCloud account and get battery and location updates for a given device.<br>
That info will then be sent to an mqtt broker using the Homie 3 convention.<br>

Required python modules:<br>
  pyicloud<br>
  Homie4<br>

TODO:<br>
  Auto re-authenticate after iCloud authentication timeout.<br>
 
How to run:<br>
  Copy icloud_homie_bridge.py to /usr/local/bin<br>
  Copy icloud_login.py to /usr/local/bin<br>
  Create a config.yaml file following the example file and put it in /etc/icloud<br>
  Copy icloud-homie-bridge.service to /usr/lib/systemd/system/<br>
  Run systemctl daemon-reload<br>
  Run systemctl enable icloud-homie-bridge.service<br>
  Run icloud_login.py (Authorizes the machine and gives a list of iCloud devices per account)<br>
  Run systemctl start icloud-homie-bridge.service<br>
  
