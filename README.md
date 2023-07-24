Download the `Revogi Petoneer Water Fountain` integration in HACS

Click add integration in the Integrations section, and select `Revogi Petoneer Water Fountain`

The integration adds a single sensor, with an overall state of the water percentage, and a number of attributes, a switch to turn the fountain on and off, and a binary sensor based around consumables alert.

Important Note: This is for fountains that use the Fresco Pro app, not the Tuya Cloud based Petoneer app.

There are 3 things required for configuration<br>
<b>username:</b> the email address used to sign in to the Fresco Pro app<br>
<b>password:</b> the password for the Fresco Pro app<br>
<b>serial:</b> the serial number for the fountain. It can be found by opening the device in the Fresco Pro app, Setting -> About

There are 4 services to reset the consumables:<br>
revogi.reset_water<br>
revogi.reset_filter<br>
revogi.reset_motor<br>
revogi.reset_all<br>

These take an entity_id of the switch created by the integration.