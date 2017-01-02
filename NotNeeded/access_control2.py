#!/usr/bin/env python

import datetime as dt
import time
import pigpio
import wiegand
from LocalDB import LocalDB
from AlarmControl import AlarmControl
from GPIOControl import GPIOControl
from Broadcaster import Broadcaster

global pi
global alarm
global gpio
global db
global bcast

def tag_scanned(bits, rfid):
    global db
    global gpio
    global alarm
    global bc
    print "Tag was scanned: %d" % rfid

    (name, allowed) = db.is_allowed(rfid)
    if (allowed):
        print "I know you, you're \"%s\". I'm letting you in" % name

        # check the status of the alarm (if armed, change)
        # gpio pin held high, gets pulled down when alarm is (??????)
        
        # if alarm has been active, then message everyone on the alarm list as well
        if alarm.is_alarm_sounding:
            alarm.toggle_alarm_pin()
            member_details = db.get_member_by_rfid(rfid)
            alert_alarm_members("Alarm has been disarmed! by %s %s " % (member_details[1], member_details[3]))

        # to change alarm, output on a gpio pin for 3 seconds
        # on(xx)
        # timeout(off,xx,seconds=3)
    
        # Beep to say you're allowed
        gpio.on(24)
        gpio.timeout(gpio.off,24,seconds=3)
        gpio.timeout(gpio.off,24,seconds=0.2)
        gpio.timeout(gpio.on,24,seconds=1)
        occupants = db.get_current_occupants()
    
        # check if they're in the local list of current occupants (sqlite)
        # Add to the list of people who are in the building (sqlite)   
        if len(occupants) is 0:
            member_details = db.get_member_by_rfid(rfid)
            bcast.alert_access_members("New Hackerspace occupant: %s %s " % (member_details[1],member_details[3]))
            if alarm.is_alarm_armed:
                alarm.toggle_alarm_pin()
            db.add_occupant(rfid)
        else:
            occupant_found = False
            for occupant in occupants:
            # if occupant has already been added to current_occupants list - don't add and don't alert anyone
                print "rfid: %s, occupant: %s" % (rfid,occupant[0])
                if rfid == occupant[0]:
                    print "Occupant already in building."
                    occupant_found = True
                # If occupant hasn't been added - add to current_occupants and alert all in 'access' list
            if occupant_found is False:
                # Send a message to anyone on the access list (access_list.access = 1)
                bcast.alert_access_members("new Hackerspace occupant: " + get_member_by_rfid(rfid)[1])
                db.add_occupant(rfid)
        
        # Add to the access log (sqlite) logging using date and civiID [3] and the date
        db.log_access_granted(rfid)
    
    else:
        print "You're not allowed in"   
        
        # Beep beep beep to say you're not allowed
        gpio.timeout(gpio.off,24,seconds=0.4)
        gpio.timeout(gpio.on,24,seconds=0.5)
        gpio.timeout(gpio.off,24,seconds=0.6)
        gpio.timeout(gpio.on,24,seconds=0.7)
        gpio.timeout(gpio.off,24,seconds=0.8)
        gpio.timeout(gpio.on,24,seconds=0.9)

        # Check to see if the tag exists and if we have a phone number
        #db = sqlite3.connect('ControlPanel.db')
        #cur = db.cursor()
        #cur.execute("SELECT name,phone,end_date FROM access_list WHERE rfid = '%s' and phone is not null" % rfid)
        #results = cur.fetchall()
        #db.close()

        # if theres a result, sms them saying they have expires on end_date

        db.log_access_denied(rfid)    

def main():
    global pi
    global db
    global alarm
    global gpio
    global bcast
    
    bcast = Broadcaster()
    db = LocalDB()
    pi = pigpio.pi()
    pi.write(24,1)   # beeper
    alarm = AlarmControl(pi)
    gpio = GPIOControl(pi)
    w = wiegand.decoder(pi, 17, 27, tag_scanned, 25)

    # interrupts for Arm ALARM button calling armAlarm
    aa = pi.callback(alarm.ARM_ALARM_BUTTON_PIN, pigpio.FALLING_EDGE, alarm.armAlarm)

    # interrupt for alarm souding armActive
    ab = pi.callback(alarm.ALARM_SOUNDING_STATUS_PIN, pigpio.FALLING_EDGE, alarm.alarmSounding)


    while True:
        time.sleep(10)

    w.cancel()
    pi.stop()

main()
