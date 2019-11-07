# icloud_homie_bridge
Bridge between iCloud device status and Homie 3 MQTT convention

I wrote this primarily to get battery and location updates from my iphone for use with openHAB, after running into too many issues with the icloud plugin.

This program will log into the specified iCloud account and get battery and location updates for a given device.
That info will then be sent to an mqtt broker using the Homie 3 convention.
