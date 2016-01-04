#!/usr/bin/env python

from apscheduler.scheduler import Scheduler
import datetime as dt
import time
import pigpio
import wiegand
import sqlite3 #debian module python-pysqlite2
import requests
import ConfigParser
import thread

sched = Scheduler()
sched.start()

global pi
global ARM_ALARM_BUTTON_PIN
global ALARM_TOGGLE_PIN
global ALARM_ARMED_STATUS_PIN
global ALARM_SOUNDING_STATUS_PIN
global DOOR_STRIKE_PIN
global arming
global is_alarm_sounding
global config

ARM_ALARM_BUTTON_PIN = 3
ALARM_TOGGLE_PIN = 10
ALARM_ARMED_STATUS_PIN = 8
ALARM_SOUNDING_STATUS_PIN = 7
DOOR_STRIKE_PIN = 22

is_alarm_sounding = False
arming = False

config = config = ConfigParser.RawConfigParser()
# ==General functionality==

# On tag scanned:
# check if user is valid
# if yes -
# 	disarm alarm
#	open door
#	add user to current_occupants table
# if nay -
#	if user is on access table, but tag has expired - send a message to them

# On alarm arm:
# clear current_occupants table
# alert alarm users

# On alarm set-off
# alert alarm people via SMS
# set alarm running to true

# == Stuff left to do: ==
# Arm alarm button callback
# Send SMS/email to important people
# Arm and disarm alarm functions - set alarm pin high/low?

# terminal logging
def print_log(message):
	outMsg = dt.datetime.strftime(dt.datetime.now(), "%a %d %b %Y %H:%M:%S: ") + str(message)
	print outMsg

def timeout(job_fn, *fn_args, **delta_args):
    """
    Usage:
        # calls `fn()` after 3 seconds
        timeout(fn, seconds=3)

        # calls `fn(foo, bar)` after 10 seconds
        timeout(fn, foor, bar, seconds=10)
    """
    the_time = dt.datetime.now() + dt.timedelta(**delta_args)
    return sched.add_date_job(job_fn, the_time, fn_args)

def is_allowed(rfid):
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    #NOTE: took out check for expiry date because my tag has expired..
    #NOTE: Also we should include a grace period, as before -Leo
    cur.execute("SELECT name FROM access_list WHERE rfid = '%s' and end_date > date('now')" % rfid)
    results = cur.fetchall()
    #cur.execute("SELECT name FROM access_list WHERE rfid = '%s'" % rfid)

    # NOTE We want to open the door first, if we're going to open it at all
    # Needs to be responsive. No delays caused by SMS, filesystem or data access please. Do that after the door's opened.

    if len(results) == 0:
        #cur.execute("SELECT name FROM access_list WHERE rfid = '%s'" % rfid)
        #results = cur.fetchall()
        #if len(results) > 0:
        #    print_log(results[0][1] + " scanned their tage to enter and their access membership has expired!")
        #    #ph = config.get('SMS', 'masterPhone')'SMS', 'masterPhone')
        #    ph = results[0][3]
        #    #message = "Hackerspace member " + results[0][1] + " tried to enter but their membership has expired."
        #    message = "Hey " + results[0][1].split(" ")[0] + ", your Hobart Hackerspace access has expired, but we're cool and will let you in for now. Please re-register on the website."
        #    send_message(ph, message)
        #    #We'll let people in for now until the notifications are sent out to expired members, and their end date is increased by a fair amount..
        #    return (results[0], True)
        db.close()
        return (None, False)
    else:
        db.close()
        return (results[0], True)

def on(pin):
    global pi
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin,1)

def off(pin):
    global pi
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin,0)

def alert_access_members(message):
	global config
	access_notify_members = get_access_notify_members()
	numbers = []
	for anm in access_notify_members:
		print_log("Hey %s, " % anm[1] + message)
		numbers.append(anm[3])

	print_log(",".join(numbers))

    #TODO: change to actual access members...
	ph = config.get('SMS', 'masterPhone')
	try:
		thread.start_new_thread(send_message, (ph, message))
	except:
		print ("Send SMS message hread failed to start for some reason..")

def alert_alarm_members(message):
    alarm_notify_members = get_alarm_notify_members()
    numbers = []
    for anm in alarm_notify_members:
        print_log("Hey %s, " % anm[1] + message)
        numbers.append(anm[3])

    print_log(",".join(numbers))
    ph = config.get('SMS', 'masterPhone')
    try:
        thread.start_new_thread(send_message, (ph, message))
    except:
        print ("Send SMS message hread failed to start for some reason..")

#TODO: Send message via email, Twitter or whatever
def send_message(numbers, message):
    # http://api.smsbrodcast.com.au/api.php?username=myuser&password=abc123&from=0400111222&to=0411222333,0422333444&message=Hello%20wor
    global config
    sms_uname = config.get('SMS', 'username')
    sms_pwd = config.get('SMS', 'password')
    url = 'http://api.smsbroadcast.com.au/api.php'
    payload = {'username': sms_uname, 'password': sms_pwd, 'from': 'Hackerspace', 'to': numbers, 'message': message}
    try:
        r = requests.get( url, params=payload )
        print_log(r.text)
    except requests.exceptions.RequestException as e:
        print e
        print_log("Error sending SMS message! Internet is probably down!")

def get_current_occupants():
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    cur.execute("SELECT rfid from current_occupants")

    results = cur.fetchall()

    db.close()

    return results

def add_occupant(rfid):
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    cur.execute("INSERT INTO current_occupants VALUES(" + str(rfid) + ")")
    db.commit()
    db.close()

def get_access_notify_members():
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    cur.execute("SELECT * FROM access_list WHERE access = 1")

    results = cur.fetchall()

    db.close()

    return results

def get_alarm_notify_members():
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    cur.execute("SELECT * FROM access_list WHERE alarm = 1")

    results = cur.fetchall()

    db.close()

    return results

def get_member_by_rfid(rfid):
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    cur.execute("SELECT * FROM access_list WHERE rfid = '%s'" % rfid)

    result = cur.fetchone()

    return result

def get_id_by_rfid(rfid):
    db = sqlite3.connect('ControlPanel.db')
    cur = db.cursor()
    cur.execute("SELECT id FROM access_list WHERE rfid = '%s'" % rfid)
    result = cur.fetchone()
    return result

def alarm_arming():
    global arming
    arming = False

# Alarm arm button callback
def armAlarm(gpio, level, tick) :
    global arming

    if arming:
        return
    arming = True
    timeout(alarm_arming,seconds=10)

    # checks alarm status
    if not is_alarm_armed():
        toggle_alarm_pin()

    # ourput buzzer for 3 seconds
    off(24)
    timeout(on,24,seconds=8)

    # clears current occupants
    # db = sqlite3.connect('ControlPanel.db')
    # cur = db.cursor()
    # cur.execute("DELETE from current_occupants")
    # db.commit()
    # db.close()

    # print_log("removed all current occupants")

    # message the access list of people
    print "Alarm is Armed"
    alert_access_members("The Alarm has been Armed")
    print

def alarmSounding(gpio, level, tick):
    global is_alarm_sounding
    #messages everyone on the alarm list (second last column)
    # set a flag so that if the alrarm is turned off by any member, it messages the entire alarm list (not just the access list)
    if not is_alarm_sounding:
        #debounce
        time.sleep(2)
        if pi.read(ALARM_SOUNDING_STATUS_PIN) == 1:
            print "debounce - bounced"
            return
        alert_alarm_members("Intruder alert: Security Alarm at the Hackerspace has been activated!")
        is_alarm_sounding = True
        print

def toggle_alarm_pin():
    global ALARM_TOGGLE_PIN
    print_log("toggling alarm pin")
    on(ALARM_TOGGLE_PIN)
    timeout(off,ALARM_TOGGLE_PIN,seconds=3)

def log_access_granted(rfid):
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    id = get_id_by_rfid(rfid)
    cur.execute("INSERT INTO access_log (id, action, synced, date) VALUES (%d, 'Access Granted', 0, DATETIME('now'))" % id)
    db.commit()
    db.close()

def log_access_denied(rfid):
    db = sqlite3.connect('ControlPanel.db')
    cur = db.cursor()

    id_row = get_id_by_rfid(rfid)
    if id_row is None:
        id = 0
    else:
        id = id_row[0]

    print_log(id)
    print_log(rfid)
    cur.execute("INSERT INTO access_log (id, action, synced, date) VALUES (%d, 'Access Denied to RFID: %d', 0, DATETIME('now'))" % (id, rfid))
    db.commit()
    db.close()

def is_alarm_armed():
    global pi
    global ALARM_ARMED_STATUS_PIN

    status = pi.read(ALARM_ARMED_STATUS_PIN) == 0
    print_log("Checking alarm, currently armed? %s" % status)

    return status

def get_member_by_rfid(rfid):
    db = sqlite3.connect('ControlPanel.db')

    cur = db.cursor()
    cur.execute("SELECT * FROM access_list WHERE rfid = '%s'" % rfid)

    result = cur.fetchone()

    return result
    return False

# tag swipe callback
def tag_scanned(bits, rfid):
    global is_alarm_sounding
    global DOOR_STRIKE_PIN

    print_log("Tag was scanned: %d" % rfid)

    (name, allowed) = is_allowed(rfid)
    if (allowed):
        print_log("I know you, you're \"%s\". I'm letting you in" % name)

        # check the status of the alarm (if armed, change)
        # gpio pin held high, gets pulled down when alarm is (??????)

        # if alarm has been acvite, then message everyone on the alarm list as well
        if is_alarm_sounding:
            member_details = get_member_by_rfid(rfid)
            #alert_alarm_members("Alarm has been disarmed! by %s %s " % (member_details[1], member_details[3]))
            is_alarm_sounding = False
            print_log("disabling alarm...")

        # to change alarm, output on a gpio pin for 3 second
        if is_alarm_armed():
            print_log("Alarm was armed, need to disarm..")
            toggle_alarm_pin()
	
        # Beep to say you're allowed
        on(DOOR_STRIKE_PIN)
        timeout(off,DOOR_STRIKE_PIN,seconds=6.5)
        timeout(off,24,seconds=0.2)
        timeout(on,24,seconds=1)
        occupants = get_current_occupants()
	
        # check if they're in the local list of current occupants (sqlite)
        # Add to the list of people who are in the building (sqlite)
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
            member_details = get_member_by_rfid(rfid)
            #alert_access_members("New Hackerspace occupant: %s %s " % (member_details[1],member_details[3]))
            # add_occupant(rfid)

        # Add to the access log (sqlite) logging using date and civiID [3] and the date
        # log_access_granted(rfid)
	
    else:
        if name is not None:
            print name + " isn't allowed in. They sould fix that!"
        else:
            print "Some random isn't allowed in"

        # Beep beep beep to say you're not allowed
        timeout(off,24,seconds=0.4)
        timeout(on,24,seconds=0.5)
        timeout(off,24,seconds=0.6)
        timeout(on,24,seconds=0.7)
        timeout(off,24,seconds=0.8)
        timeout(on,24,seconds=0.9)

        # Check to see if the tag exists and if we have a phone number
        db = sqlite3.connect('ControlPanel.db')
        cur = db.cursor()
        cur.execute("SELECT name,phone,end_date FROM access_list WHERE rfid = '%s' and phone is not null" % rfid)
        results = cur.fetchall()
        db.close()

        # if theres a result, sms them saying they have expires on end_date
        # log_access_denied(rfid)

    print


def main():
    global pi
    global config
    config.read('/home/pi/access_control/config.cfg')
    pi = pigpio.pi()
    pi.write(24,1)
    w = wiegand.decoder(pi, 27, 17, tag_scanned, 25)

    # interrupts for Arm ALARM button calling armAlarm
    aa = pi.callback(ARM_ALARM_BUTTON_PIN, pigpio.FALLING_EDGE, armAlarm)

    # interrupt for alarm souding armActive
    ab = pi.callback(ALARM_SOUNDING_STATUS_PIN, pigpio.FALLING_EDGE, alarmSounding)
    
    while True:
        time.sleep(10)

    w.cancel()
    pi.stop()

main()
