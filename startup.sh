#!/bin/sh
runuser -l pi -c "/usr/bin/screen -dmS doorman /usr/bin/python2 /home/pi/HHSAccessControl/access_control.py"
