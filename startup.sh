#!/bin/sh
runuser -l leo -c "/usr/bin/screen -dmS doorman /usr/bin/python2 /home/pi/HHSAccessControl/access_control.py"
