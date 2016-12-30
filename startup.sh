#!/bin/sh
runuser -l pi -c 'cd /home/pi/HHSAccessControl; screen -dmS doorman python /home/pi/HHSAccessControl/access_control.py'
